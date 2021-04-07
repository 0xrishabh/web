# -*- coding: utf-8 -*-
"""Handle marketing mail related tests.

Copyright (C) 2020 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


"""
*********
CONTROLLER LOGIC 4 Quadratic Lands Initial Distribution--)> 
*********
"""


import binascii
import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

import requests
from dashboard.models import Profile
from eth_utils import is_address, is_checksum_address, to_checksum_address
from quadraticlands.models import InitialTokenDistribution, MissionStatus, QuadLandsFAQ
from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)
   
def get_FAQ(request):
    '''Get FAQ objects from the db and bundle them up to be added to faq context'''
    faq_dict = {}
    full_faq = {}
    item = {}

    try:
        faq = QuadLandsFAQ.objects.all()
    except Exception as e:
        logger.info(f'QuadLands - There was an issue getting FAQ DB object - {e}')
        faq = False
    
    for faq_item in faq:
        item = {
            'question' : faq_item.question,
            'answer' : faq_item.answer
        }
        faq_dict[str(faq_item.position)] = item 
        
    full_faq['FAQ'] = faq_dict
    
    return full_faq

def get_profile_from_username(request):
    '''Return profile object for a given request'''
    try:  
        profile = Profile.objects.get(handle=request.user.username)
    except Exception as e:
        logger.info(f'QuadLands - There was an issue getting user profile object - {e}')
        profile = False 
    return profile 

@require_http_methods(["GET"])
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def get_mission_status(request):
    '''Retrieve mission status/state from the DB'''
    if request.user.is_authenticated:        
        profile = get_profile_from_username(request)
        try: 
            mission_status = MissionStatus.objects.get(profile=profile)
            game_state = {
                "id" : mission_status.id,
                "proof_of_use" : mission_status.proof_of_use,
                "proof_of_knowledge" : mission_status.proof_of_knowledge,
                "proof_of_receive" : mission_status.proof_of_receive,
            }
            return game_state
        except MissionStatus.DoesNotExist:
            pass

    # if state doesn't exist yet or user is not logged in
    no_game_state = {
        "id" : False,
        "proof_of_use" : False,
        "proof_of_knowledge" : False,
        "proof_of_receive" : False
    }
    return no_game_state


@require_http_methods(["POST"])
@login_required
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def set_mission_status(request):
    '''When a mission is completed, the UI will POST here to flip game state completed True for a given mission'''
    if request.user.is_authenticated:
        try: 
            mission_name = request.POST.get('mission')
            if type(mission_name) != str:
                logger.info('QuadLands - Non-string received for mission_name.')
                HttpResponse(status=404)
            elif mission_name not in ('proof_of_use', 'proof_of_knowledge','proof_of_receive'):
                logger.info(f'QuadLands - Invalid mission_name received - {mission_name}')
                HttpResponse(status=404)
        except:
            logger.info('QuadLands - Failed to parse set_mission_status')
            return HttpResponse(status=404)
        
        profile = get_profile_from_username(request)

        # fix this - it's working but not ideal 
        # if doesn't exist creates record 
        mission = MissionStatus.objects.get_or_create(profile=profile)
        # then get the record 
        mission_status = MissionStatus.objects.get(profile=profile)
     
        if mission_name == 'proof_of_knowledge':
            mission_status.proof_of_knowledge = True  
            mission_status.save() 
            return HttpResponse(status=200)
        
        if mission_name == 'proof_of_use': 
            mission_status.proof_of_use = True
            mission_status.save()
            return HttpResponse(status=200)
        
        if mission_name == 'proof_of_receive': 
            mission_status.proof_of_receive = True
            mission_status.save()
            return HttpResponse(status=200)
        

def get_initial_dist(request):
    '''Accpets request, returns initial dist info from the DB in units WEI & GTC'''
    no_claim = {"total_claimable_gtc": 0, "total_claimable_wei": 0}
    if not request.user.is_authenticated:
        return no_claim

    profile = get_profile_from_username(request)
    try:   
        initial_dist_wei = InitialTokenDistribution.objects.get(profile=profile).claim_total
        initial_dist_gtc = initial_dist_wei / 10**18
        context = {
            'total_claimable_gtc': initial_dist_gtc, 
            'total_claimable_wei': initial_dist_wei
        }
    except InitialTokenDistribution.DoesNotExist: # if user doesn't have a token claim record in DB 
        context = no_claim

    return context


@require_http_methods(["POST"])
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def claim(request):
    '''
    Receives AJAX post from CLAIM button on claim.html 
    Returns JSON response (signed token claim!) from Eth Signed Message Service
    '''
    if request.user.is_authenticated:
         
        profile = get_profile_from_username(request)
        logger.info(f'claim profile id: {profile.id}')  

        post_data_to_emss = {}
        post_data_to_emss['user_id'] = profile.id
       
        # confirm we received a valid, checksummed address for the token claim
        # then add address to post_data_to_emss dict 
        try:
            if is_checksum_address(request.POST.get('address')):
                post_data_to_emss['user_address'] = request.POST.get('address')
            elif is_address(request.POST.get('address')):
                post_data_to_emss['user_address'] = to_checksum_address(request.POST.get('address'))
            else:
                logger.info('QuadLands: token claim address failed integrity check. No claim will be generated.')
                return JsonResponse({'error': 'Token claim address failed integrity checks.'})
        except:
            logger.error('QuadLands: There was an issue validating user wallet address.')
            return JsonResponse({'error': 'Token claim address failed validation'})
        
        # confirm we received a valid, checksummed delegate address for the token claim
        # then add address to post_data_to_emss dict 
        try:
            if is_checksum_address(request.POST.get('delegate')):
                post_data_to_emss['delegate_address'] = request.POST.get('delegate')
            elif is_address(request.POST.get('delegate')):
                post_data_to_emss['delegate_address'] = to_checksum_address(request.POST.get('delegate'))
            else:
                logger.info('QuadLands: token claim delegate_address failed integrity check. No claim will be generated.')
                return JsonResponse({'error': 'Token claim delegate failed integrity checks.'})
        except:
            logger.error('QuadLands: There was an issue validating delegate address.')
            return JsonResponse({'error': 'Token claim delegate failed validation'})
          
        claim = get_initial_dist(request)

        post_data_to_emss['user_amount'] = claim['total_claimable_wei'] 
             
        # create a hash of post data
        try:                 
            sig = create_sha256_signature(settings.GTC_DIST_KEY, json.dumps(post_data_to_emss))
        except: 
            logger.error('QuadLands: Error creating hash of POST data for EMSS')
            return JsonResponse({'error': 'Creating hashing token claim data.'})

        header = { 
            "X-GITCOIN-SIG" : sig,
            "content-type": "application/json",
        }
    
        # POST relevant user data to micro service that returns signed transation data for the user broadcast
        # TODO - need to improve error = TRUE stuff here. what should we send back to UI if esms is down?   
        try: 
            emss_response = requests.post(settings.GTC_DIST_API_URL, data=json.dumps(post_data_to_emss), headers=header)
            # emss_response = requests.post('http://10.1.10.10:5000/v1/sign_claim', data=json.dumps(post_data_to_emss), headers=header)
            emss_response_content = emss_response.content
            # logger.info(f'GTC Distributor: emss_response_content: {emss_response_content}')
            emss_response.raise_for_status() # raise exception on error 
        except requests.exceptions.ConnectionError:
            logger.error('GTC Distributor: ConnectionError while connecting to EMSS!')
            resp = {'ERROR': 'There was an issue getting token claim.'}
            return JsonResponse(resp)
        except requests.exceptions.Timeout:
            # Maybe set up for a retry
            logger.error('GTC Distributor: Timeout while connecting to EMSS!')
            resp = {'ERROR': 'There was an issue getting token claim.'}
            return JsonResponse(resp)
        except requests.exceptions.TooManyRedirects:
            logger.error('GTC Distributor: Too many redirects while connecting to EMSS!')
            resp = {'ERROR': 'There was an issue getting token claim.'}
            return JsonResponse(resp)
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            logger.error(f'GTC Distributor:  Error posting to EMSS - {e}')
            resp = {'ERROR': 'There was an issue getting token claim.'}
            return JsonResponse(resp)

        # pass returned values from eth signer microservice
        # ESMS returns bytes object of json. so, we decode it
        esms_response = json.loads( emss_response_content.decode('utf-8'))
        # construct nested dict for easy access in templates

        logger.info(f'GTC Token Distributor - ESMS response: {esms_response}') 
        return JsonResponse(esms_response)
    else:
        logger.info('Non authenticated request sent to claim - highly sus - request ignored.')
        raise Http404

def create_sha256_signature(key, message):
    '''Given key & message, returns HMAC digest of the message'''
    try:
        byte_key = binascii.unhexlify(key)
        message = message.encode()
        return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()
    except Exception as e:
        logger.error(f'GTC Distributor - Error Hashing Message: {e}')
        return False 

