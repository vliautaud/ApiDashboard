from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse,HttpResponseForbidden,HttpResponseRedirect,QueryDict,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
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
import uuid
import logging

logger = logging.getLogger(__name__)


###################################################################
# Traitement des webhooks
###################################################################
@csrf_exempt
def webhook(request):
    logger.debug("Debut traitement du webhook...")
    # Contrôle WebHook Post
    if (request.method == "POST") :
        try :
            webhook_event=request.META["HTTP_X_OSP_WEBHOOK_EVENT_NAME"]
            if webhook_event=="orderCancelled" :
                return orderCancelled(request,webhook_event)
            else :
                HttpResponseForbidden("Type de webhook non pris en charge...")
        except Exception as err :
            return HttpResponseBadRequest("Erreur interne traitement de Webhook :"+str(err))
    else :
        return HttpResponseForbidden("Methode POST obligatoire...")


def orderCancelled(request,webhook_event):
    logger.debug("Debut traitement du webhook orderCanceled...")
    try :
        webhook_body=json.loads(request.body.decode("utf-8"))
        baseURL = myconf["ENV_PROD_BASEURL"]
        osp_session = OcadoSession.OcadoSession(
            urlAccessToken=myconf["ENV_PROD_ACCESS_TOKEN"],
            clientId=myconf["ENV_PROD_CLIENT_ID"],
            clientSecret=myconf["ENV_PROD_CLIENT_SECRET"],
            apiKey=myconf["ENV_PROD_APIKEY"],
            proxy=dict(eval(myconf["PROXY"])))
        res,head=osp_session.get(baseURL+"/v3/"+webhook_body["retailerBannerId"]+"/orders/"+webhook_body["orderId"],str(uuid.uuid1()))
        cancelationReason=res.json()["cancellationReasonId"]
        if cancelationReason == "FAILED_DELIVERY" :
            # Envoi du mail
            vil_tools.send_mail("noreply@ologistique.fr",
                            myconf["MAIL_DEST"].split(";"),
                            "Annulation de commande : " + webhook_body["orderId"] + " le " + datetime.datetime.now().strftime(
                                "%Y/%m/%d"),
                            message_text="",
                            files=[],
                            server=myconf["MAIL_SMTP"],
                            port=myconf["MAIL_PORT"],
                            username=myconf["MAIL_USER"],
                            password=myconf["MAIL_PWD"],
                            message_html=template % (webhook_body["orderId"], datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")),
                            embeddedImages={"image1": settings.BASE_DIR+"/dashboard/static/dashboard/images/logoOlog.jpg"}    )

        return HttpResponse("Webhook de type %s et body %s cancellationReason %s" % (str(webhook_event),webhook_body["orderId"],cancelationReason))
        #return HttpResponse()
    except Exception as err :
        return HttpResponseBadRequest("Erreur interne traitement de Webhook :"+ webhook_event +" : Exception : "+ str(err))

# ##########################################################################
# Main : Au chargement du module => On charge le fichier de conf de l'appli
# ##########################################################################
myconf=vil_tools.fwk_init(settings.BASE_DIR+"/dashboard/conf/ocado.cfg")   # Recuperation des parametres de config

template="""
<html>
   </style><![endif]-->
   <style>
      <!--
         /* Font Definitions */
         @font-face
                {font-family:"Cambria Math";
                panose-1:2 4 5 3 5 4 6 3 2 4;}
         @font-face
                {font-family:Calibri;
                panose-1:2 15 5 2 2 2 4 3 2 4;}
         /* Style Definitions */
         p.MsoNormal, li.MsoNormal, div.MsoNormal
                {margin:0cm;
                margin-bottom:.0001pt;
                font-size:11.0pt;
                font-family:"Calibri",sans-serif;
                mso-fareast-language:EN-US;}
         a:link, span.MsoHyperlink
                {mso-style-priority:99;
                color:#0563C1;
                text-decoration:underline;}
         a:visited, span.MsoHyperlinkFollowed
                {mso-style-priority:99;
                color:#954F72;
                text-decoration:underline;}
         span.EmailStyle17
                {mso-style-type:personal;
                font-family:"Calibri",sans-serif;
                color:windowtext;}
         .MsoChpDefault
                {mso-style-type:export-only;
                font-family:"Calibri",sans-serif;
                mso-fareast-language:EN-US;}
         @page WordSection1
                {size:612.0pt 792.0pt;
                margin:70.85pt 70.85pt 70.85pt 70.85pt;}
         div.WordSection1
                {page:WordSection1;}
         -->
   </style>
   </head>
   <body lang=FR link="#0563C1" vlink="#954F72">
      <div class=WordSection1>
         <p class=MsoNormal>
            Bonjour,

         </p>
         <p class=MsoNormal>
            <o:p>&nbsp;</o:p>
         </p>
         <p class=MsoNormal>
            La commande suivante vient d&#8217;être annulée&nbsp;:
            <o:p></o:p>
         </p>
         <table class=MsoTable15List3Accent6 border=1 cellspacing=0 cellpadding=0 style='border-collapse:collapse;border:none'>
            <tr>
               <td width=313 valign=top style='width:234.9pt;border-top:solid #70AD47 1.0pt;border-left:solid #70AD47 1.0pt;border-bottom:none;border-right:none;background:#70AD47;padding:0cm 5.4pt 0cm 5.4pt'>
                  <p class=MsoNormal>
                     <b>
                        <span style='color:white'>
                           N° de commande
                           <o:p></o:p>
                        </span>
                     </b>
                  </p>
               </td>
               <td width=313 valign=top style='width:234.9pt;border-top:solid #70AD47 1.0pt;border-left:none;border-bottom:none;border-right:solid #70AD47 1.0pt;background:#70AD47;padding:0cm 5.4pt 0cm 5.4pt'>
                  <p class=MsoNormal>
                     <b>
                        <span style='color:white'>
                           Date/Heure
                           <o:p></o:p>
                        </span>
                     </b>
                  </p>
               </td>
            </tr>
            <tr>
               <td width=313 valign=top style='width:234.9pt;border:solid #70AD47 1.0pt;border-right:none;background:white;padding:0cm 5.4pt 0cm 5.4pt'>
                  <p class=MsoNormal>
                     <b>
                        %s
                        <o:p></o:p>
                     </b>
                  </p>
               </td>
               <td width=313 valign=top style='width:234.9pt;border:solid #70AD47 1.0pt;border-left:none;padding:0cm 5.4pt 0cm 5.4pt'>
                  <p class=MsoNormal>
                     %s
                     <o:p></o:p>
                  </p>
               </td>
            </tr>
         </table>
         <p class=MsoNormal>
        <span style='mso-fareast-language:FR'><img width=138 height=85  src="cid:image1"></span>
      </div>
   </body>
</html>
"""