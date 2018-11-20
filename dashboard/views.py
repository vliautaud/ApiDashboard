from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse,HttpResponseRedirect,QueryDict
from django.urls import reverse
from .models import ApiCall
from django.db.models import Count
import dashboard.viltools.paginatorVil as paginatorVil
import dashboard.viltools.vil_tools as vil_tools
import dashboard.viltools.OcadoSession as OcadoSession
import json
import csv
import pytz
from django.contrib.auth import  logout
from django.utils import timezone
from django.conf import settings
import datetime


# ####################################################################
# Vue Dashboard
# ####################################################################
# Create your views here.
@login_required(login_url='/ocado/accounts/login/')
def dashboard(request):
    # Enregistrement du dictionnaire dans la session
    if request.session.get("DICT",False) :
        myconf=request.session.get("DICT", False)
    else :
        myconf = vil_tools.fwk_init(settings.BASE_DIR+"/dashboard/conf/ocado.cfg")  # Recuperation des parametres de config
        request.session["DICT"] = myconf

    #Sauvegarde des criteres de recherche + numero de page en contexte de session
    #Le seul POST c'est quand on relance un SEARCH (tout le reste on est en GET)
    if request.POST :
        dict_context=dict(request.POST.items())
        dict_context["page"]="1"
        request.session["CONTEXT"] = dict_context
    else :
        dict_context=dict(request.session.get("CONTEXT",{}).items())
        dict_context.update(dict(request.GET.items()))
        request.session["CONTEXT"] = dict_context


    where_clause = {}
    if dict_context.get("VERBE") :
        where_clause.update({"api_verbe__exact":dict_context.get("VERBE")})
    if dict_context.get("USER") :
        where_clause.update({"api_user__contains":dict_context.get("USER")})
    if dict_context.get("URL") :
        where_clause.update({"api_url__contains":dict_context.get("URL")})
    if dict_context.get("DDEB") :
        jour,mois,annee=int(dict_context.get("DDEB")[0:2]),int(dict_context.get("DDEB")[3:5]),int(dict_context.get("DDEB")[6:10])
        where_clause.update({"api_call_date__gt": datetime.datetime(annee, mois, jour,tzinfo=pytz.UTC)})
    if dict_context.get("DFIN") :
        jour,mois,annee=int(dict_context.get("DFIN")[0:2]),int(dict_context.get("DFIN")[3:5]),int(dict_context.get("DFIN")[6:10])
        where_clause.update({"api_res_date__lt": datetime.datetime(annee, mois, jour,23,59,59,tzinfo=pytz.UTC)})

    # Gestion affichage du nombre de Get/PUT/POST/DELETE
    nb_get_calls, nb_put_calls, nb_post_calls, nb_delete_calls=0,0,0,0
    if where_clause.get("api_verbe__exact")=="GET" :
        nb_get_calls = len(ApiCall.objects.filter(**where_clause))
    elif  where_clause.get("api_verbe__exact")=="PUT" :
        nb_put_calls = len(ApiCall.objects.filter(**where_clause))
    elif where_clause.get("api_verbe__exact")=="POST" :
        nb_post_calls = len(ApiCall.objects.filter(**where_clause))
    elif where_clause.get("api_verbe__exact")=="DELETE" :
        nb_delete_calls = len(ApiCall.objects.filter(**where_clause))
    else :
        nb_get_calls=len(ApiCall.objects.filter(**where_clause,api_verbe__exact="GET"))
        nb_put_calls = len(ApiCall.objects.filter(**where_clause,api_verbe__exact="PUT"))
        nb_post_calls = len(ApiCall.objects.filter(**where_clause,api_verbe__exact="POST"))
        nb_delete_calls = len(ApiCall.objects.filter(**where_clause,api_verbe__exact="DELETE"))
    codes_ret = ApiCall.objects.filter(**where_clause).values("api_res_retcode").annotate(Count("id")).order_by()
    latest_calls = ApiCall.objects.filter(**where_clause).order_by('-api_call_date')[:10000]

    paginator = paginatorVil.PaginatorVil(latest_calls, 10)  # N lignes par pages
    page = request.GET.get('page',dict_context.get("page"))
    if page!=None :
        latest_calls = paginator.get_page(page)
        page_list=paginator.getPageListby5(page)
    else:
        latest_calls = paginator.get_page(1)
        page_list = paginator.getPageListby5(1)

    context = {'latest_calls': latest_calls,
               'codes_ret' : codes_ret,
               'page_list' : page_list,
               'nb_get' : nb_get_calls,
               'nb_put': nb_put_calls,
               'nb_post': nb_post_calls,
               'nb_delete': nb_delete_calls,
               'SEARCH' : dict_context,
               }

    return render(request, 'dashboard/OcadoDashboard.htm',context)


###################################################################
# VUE client_api
###################################################################
@login_required(login_url='/ocado/accounts/login/')
def client_api(request):
    return client_api_id(request,"")

###################################################################
# VUE client_api
###################################################################
@login_required(login_url='/ocado/accounts/login/')
def client_api_id(request,api_call_id):
    # On est en POST => Demande appel API
    if (request.POST) :
        # Mise en session de l'objet  OcadoSession si existe pas déjà
        if request.POST.get("optionsRadiosEnv") in ["SANDBOX","TEST","PROD"] :
            # Si environnement selectionné correctement configuré
            if myconf["ENV_"+request.POST.get("optionsRadiosEnv")+"_BASEURL"]:
                # Si OcadoSession  pas dans la session utilisateur => On le crée
                baseURL = myconf["ENV_"+request.POST.get("optionsRadiosEnv")+"_BASEURL"]
                if request.POST.get("optionsRadiosEnv") not in request.session :
                    print("CREATION "+request.POST.get("optionsRadiosEnv")+" SESSION DANS SESSION")
                    sandbox_session = OcadoSession.OcadoSession(urlAccessToken=myconf["ENV_"+request.POST.get("optionsRadiosEnv")+"_ACCESS_TOKEN"],
                                                                clientId=myconf["ENV_"+request.POST.get("optionsRadiosEnv")+"_CLIENT_ID"],
                                                                clientSecret=myconf["ENV_"+request.POST.get("optionsRadiosEnv")+"_CLIENT_SECRET"],
                                                                apiKey=myconf["ENV_"+request.POST.get("optionsRadiosEnv")+"_APIKEY"],
                                                                proxy=dict(eval(myconf["PROXY"])))
                    request.session[request.POST.get("optionsRadiosEnv")] = sandbox_session
            else : # Environnement non configuré dans ficher de conf => On retourne une erreur
                context = {'FORM': request.POST,'ERROR' : "Environnement "+request.POST.get("optionsRadiosEnv")+" non disponible !!!"}
                return render(request, 'dashboard/OcadoFormCallApi.htm', context)

        # Récupération du Payload JSON
        myPayload = {}
        payload=""
        if request.POST.get("PAYLOAD") :
            try:
                payload = json.loads(request.POST.get("PAYLOAD"))
                #payload = request.POST.get("PAYLOAD")
                myPayload = {"json": payload}
            except:
                print("Payload impossible à parser :",request.POST.get("PAYLOAD"))
                context = {'FORM': request.POST, 'ERROR': "Impossible de parser le PAYLOAD JSON - Veuillez corriger !!!"}
                return render(request, 'dashboard/OcadoFormCallApi.htm', context)
        # A ce stade : Tout semble Ok => On récupère le bon objet OcadoSession et on lance l'API
        ocadoSession = request.session[request.POST.get("optionsRadiosEnv")]
        try :
            if request.POST.get("optionsRadiosVerbe")=="GET" :
                dateheuredeb=timezone.now()
                res = ocadoSession.get(baseURL+request.POST.get("URL").strip(),"TESTVLD"+str(timezone.now()),**myPayload)
                dateheurefin = timezone.now()
            elif request.POST.get("optionsRadiosVerbe")=="PUT" :
                dateheuredeb =timezone.now()
                res = ocadoSession.put(baseURL + request.POST.get("URL").strip(), "TESTVLD" + str(timezone.now()),**myPayload)
                dateheurefin = timezone.now()
            elif request.POST.get("optionsRadiosVerbe") == "POST":
                dateheuredeb = timezone.now()
                res = ocadoSession.put(baseURL + request.POST.get("URL").strip(), "TESTVLD" + str(timezone.now()),**myPayload)
                dateheurefin = timezone.now()
            elif request.POST.get("optionsRadiosVerbe") == "DELETE":
                dateheuredeb = timezone.now()
                res = ocadoSession.put(baseURL + request.POST.get("URL").strip(), "TESTVLD" + str(timezone.now()),**myPayload)
                dateheurefin = timezone.now()
            else :
                context = {'FORM': request.POST, 'ERROR': "Erreur grave : ni Get, ni PUT, ni POST, ni DELETE !!!"}
                return render(request, 'dashboard/OcadoFormCallApi.htm', context)
        except :
            context = {'FORM': request.POST, 'ERROR': "Erreur grave : lors de l'appel de l'API!!! Veuillez vérifier que l'URL démarre par '/' et consultez la log" }
            return render(request, 'dashboard/OcadoFormCallApi.htm', context)


        # A ce stade l'appel JSON est OK
        # Création et sauvegarde d'un objet ApiCall
        appel_api=ApiCall()
        appel_api.api_call_date = dateheuredeb
        appel_api.api_res_date = dateheurefin
        appel_api.api_verbe = request.POST.get("optionsRadiosVerbe")
        appel_api.api_env = request.POST.get("optionsRadiosEnv")
        appel_api.api_user = request.user.username
        appel_api.api_url = baseURL+request.POST.get("URL").strip()
        appel_api.api_prefix_url = baseURL
        appel_api.api_suffix_url = request.POST.get("URL").strip()
        appel_api.api_header = "TODO : creer getheader sur objet OcadoSession"
        appel_api.api_payload = request.POST.get("PAYLOAD")
        appel_api.api_res_retcode = res.status_code
        appel_api.api_res_header = res.headers
        appel_api.api_res_body = res.text
        appel_api.save()
        return HttpResponseRedirect(reverse('ocado:client_api_id',args=(appel_api.id,)))
    # Else, Request = GET
    else :
        # GET : Réaffichage d'une API
        if api_call_id :
            api_call=get_object_or_404(ApiCall, pk=api_call_id)
            context={'FORM' : { "optionsRadiosEnv" : api_call.api_env,
                                "optionsRadiosVerbe": api_call.api_verbe,
                                "URL" : api_call.api_suffix_url,
                                "PAYLOAD" : api_call.api_payload,
                                "RET_CODE": api_call.api_res_retcode,
                                "RES_HEADER": api_call.api_res_header,
                                "RES_JSON" : api_call.api_res_body }
                     }
        # GET : Affichage à vide (appel initial)
        else :
            context={}
        return render(request, 'dashboard/OcadoFormCallApi.htm',context)


###################################################################
# VUE remove_api_call
###################################################################
@login_required(login_url='/ocado/accounts/login/')
def remove_api_call(request):
    api_call = get_object_or_404(ApiCall, pk=request.POST.get("api_call_id"))
    api_call.delete()
    return HttpResponseRedirect(reverse('ocado:dashboard'))


@login_required(login_url='/ocado/accounts/login/')
def client_api(request):
    return client_api_id(request,"")



###################################################################
# VUE bug_report
###################################################################
@login_required(login_url='/ocado/accounts/login/')
def bug_report(request,api_call_id):
    appel_api = get_object_or_404(ApiCall, pk=api_call_id)
    context = {
                'api_call_date' : appel_api.api_call_date,
                'api_res_date' : appel_api.api_res_date ,
                'api_verbe' : appel_api.api_verbe ,
                'api_env'  : appel_api.api_env ,
                'api_user' : appel_api.api_user ,
                'api_url' : appel_api.api_url,
                'api_header' : appel_api.api_header ,
                'api_payload' : appel_api.api_payload ,
                'api_res_retcode'  : appel_api.api_res_retcode ,
                'api_res_header' : appel_api.api_res_header ,
                'api_res_body' : appel_api.api_res_body
              }
    return render(request, 'dashboard/bugreport.txt',context,content_type='text/plain')


###################################################################
# VUE exportcsv
###################################################################
@login_required(login_url='/ocado/accounts/login/')
def exportcsv(request):
    dict_context = dict(request.session.get("CONTEXT", {}).items())
    response=HttpResponse(content_type='text\csv')
    response['Content-Disposition']='attachment ; filename="export_api_call.csv"'
    #Si criteres de recherches stockees en session sont renseignés
    where_clause = {}
    if dict_context.get("VERBE"):
        where_clause.update({"api_verbe__exact": dict_context.get("VERBE")})
    if dict_context.get("USER"):
        where_clause.update({"api_user__contains": dict_context.get("USER")})
    if dict_context.get("URL"):
        where_clause.update({"api_url__contains": dict_context.get("URL")})
    if dict_context.get("DDEB"):
        jour, mois, annee = int(dict_context.get("DDEB")[0:2]), int(dict_context.get("DDEB")[3:5]), int(
            dict_context.get("DDEB")[6:10])
        where_clause.update({"api_call_date__gt": datetime.datetime(annee, mois, jour, tzinfo=pytz.UTC)})
    if dict_context.get("DFIN"):
        jour, mois, annee = int(dict_context.get("DFIN")[0:2]), int(dict_context.get("DFIN")[3:5]), int(
            dict_context.get("DFIN")[6:10])
        where_clause.update({"api_res_date__lt": datetime.datetime(annee, mois, jour, 23, 59, 59, tzinfo=pytz.UTC)})

    latest_calls = ApiCall.objects.filter(**where_clause).order_by('-api_call_date')
    # Ecriture du CSV
    # TODO : A retravailler pour batir fonction générique en fonction d'une liste QueryResult
    writer=csv.writer(response,delimiter=';')
    writer.writerow(['CALLID','DDEB_CALL','DFIN_CALL','USER','ENV','VERBE','URL','RET_CODE'])
    for api_call in latest_calls :
        writer.writerow([api_call.id,api_call.api_call_date,api_call.api_res_date,api_call.api_user,
                         api_call.api_env,api_call.api_verbe,api_call.api_suffix_url,api_call.api_res_retcode])

    return response


# ###############################################################
# Vue Logout
# ###############################################################
def ocado_logout(request):
    logout(request)
    return render(request, 'dashboard/OcadoLogout.htm')

# ##########################################################################
# Main : Au chargement du module => On charge le fichier de conf de l'appli
# ##########################################################################
myconf=vil_tools.fwk_init(settings.BASE_DIR+"/dashboard/conf/ocado.cfg")   # Recuperation des parametres de config
