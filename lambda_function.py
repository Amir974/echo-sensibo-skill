"""
This it my independant voice control skill app for alexa
developed by Amir Hanan

"""
from __future__ import print_function
import requests
import json

_SERVER = 'https://home.sensibo.com/api/v2'

""" This skill is designed for only one pod at the moment / the first pod listed on your account 
(since I don't have multiple pods, I could not design / test the app for this scenario 
but it's should be relatively easy to make the adjustment... """
my_api_key_default = 'please copy to my_api_key the key you got using sensibo web app'

my_api_key = my_api_key_default # change this to string with your API key 'something something something'


""" Sensibo Object type """
class SensiboClientAPI(object):
	def __init__(self, api_key):
		self._api_key = api_key

	def _get(self, path, ** params):
		params['apiKey'] = self._api_key
		response = requests.get(_SERVER + path, params = params)
		response.raise_for_status()
		return response.json()

	def _post(self, path, data, ** params):
		params['apiKey'] = self._api_key
		response = requests.post(_SERVER + path, params = params, data = data)
		response.raise_for_status()
		return response.json()

	def pod_uids(self):
		result = self._get("/users/me/pods")
		pod_uids = [x['id'] for x in result['result']]
		return pod_uids

	def pod_measurement(self, podUid):
		result = self._get("/pods/%s/measurements" % podUid)
		return result['result']

	def pod_ac_state(self, podUid):
		result = self._get("/pods/%s/acStates" % podUid, limit = 1, fields="status,reason,acState")
		return result['result'][0]

	def pod_change_ac_state(self, podUid, on, target_temperature, mode, fan_level):
		self._post("/pods/%s/acStates" % podUid,
				json.dumps({'acState': {"on": on, "targetTemperature": target_temperature, "mode": mode, "fanLevel": fan_level}}))
					
				
def lambda_handler(event, context):
	""" Route the incoming request based on type (LaunchRequest, IntentRequest,
	etc.) The JSON body of the request is provided in the event parameter.
	"""

	print("event.session.application.applicationId=" +
		  event['session']['application']['applicationId'])
	
	"""
	Uncomment this if statement and populate with your skill's application ID to
	prevent someone else from configuring a skill that sends requests to this
	function.
	"""
	# if (event['session']['application']['applicationId'] !=
	#         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
	#     raise ValueError("Invalid Application ID")

	if event['session']['new']:
		on_session_started({'requestId': event['request']['requestId']},
						   event['session'])

	if event['request']['type'] == "LaunchRequest":
		return on_launch(event['request'], event['session'])
	elif event['request']['type'] == "IntentRequest":
		return on_intent(event['request'], event['session'])
	elif event['request']['type'] == "SessionEndedRequest":
		return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
	""" Called when the session starts """
	#print ("* on_session_started")

	print("on_session_started requestId=" + session_started_request['requestId']
		  + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
	""" Called when the user launches the skill without specifying what they
	want
	"""
	#print ("* on_launch")

	print("on_launch requestId=" + launch_request['requestId'] +
		  ", sessionId=" + session['sessionId'])
	# Dispatch to your skill's launch
	return get_welcome_response(session)


def on_intent(intent_request, session):
	""" Called when the user specifies an intent for this skill """
	#print ("* on_intent")

	print("on_intent requestId=" + intent_request['requestId'] +
		  ", sessionId=" + session['sessionId'])

	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']

	# Dispatch to your skill's intent handlers
	if intent_name == "GetStatusIntent":
		return get_room_status_from_session(intent, session)
	elif intent_name == "GetSettingsIntent":
		return get_settings_status_from_session(intent, session)
	elif intent_name == "GetFullIntent":
		return get_full_status_from_session(intent, session)
	elif intent_name == "SetTempIntent":
		return set_temp_in_session(intent, session)
	elif intent_name == "SetModeIntent":
		return set_mode_in_session(intent, session)
	elif intent_name == "SetFanIntent":
		return set_fan_in_session(intent, session)
	elif intent_name == "SetAllIntent":
		return set_all_in_session(intent, session)
	elif intent_name == "IncreaseIntent":
		return set_inc_temp_in_session(intent, session)
	elif intent_name == "DecreaseIntent":
		return set_dec_temp_in_session(intent, session)
	elif intent_name == "TurnOnIntent":
		return set_turnon(intent, session)
	elif intent_name == "ShutdownIntent":
		return set_shutdown(intent, session)
	elif intent_name == "HelpIntent":
		return get_help(intent, session)
	elif intent_name == "ResetIntent":
		return reset_response(session)
	else:
		raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
	""" Called when the user ends the session.
	Is not called when the skill returns should_end_session=true
	"""
	#print ("* on_session_ended")

	print("on_session_ended requestId=" + session_ended_request['requestId'] +
		  ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response(session):
	""" If we wanted to initialize the session to have some attributes we could
	add those here
	"""
	#print ("* get_welcome_response")
	if my_api_key == my_api_key_default:
		session_attributes = {}
		speech_output = "Sensibo app disabled, " \
			"please assign your unique API key into my_api_key inside the code, " \
			"check installation instruction for details"
		# If the user either does not reply to the welcome message or says something
		# that is not understood, they will be prompted again with this text.
		reprompt_text = None
		should_end_session = True
	
	else:
		session_attributes = session.get('attributes', {})
		
		"""
		Loading Sensibo info to session attributes
		"""
		client = SensiboClientAPI(my_api_key)
		pod_uids = client.pod_uids()
		last_ac_state = client.pod_ac_state(pod_uids[0])
		currMsr = client.pod_measurement(pod_uids[0])
		
		if last_ac_state['acState']['on'] :
			my_last_ac_state = "on"
		else:
			my_last_ac_state = "off"
			
		if last_ac_state['acState']['temperatureUnit'] == 'C' :
			my_temp_type = "Celsius"
		else:
			my_temp_type = "Fahrenheit"
			
		session_attributes = create_current_action_attributes(last_ac_state['acState']['mode'],	last_ac_state['acState']['targetTemperature'],last_ac_state['acState']['fanLevel'],currMsr[0]['temperature'],currMsr[0]['humidity'],my_last_ac_state,my_temp_type)
		
		speech_output = "Sensibo on." 
		# If the user either does not reply to the welcome message or says something
		# that is not understood, they will be prompted again with this text.
		reprompt_text = "Please let me know what you want me to do, " \
							"If you are unsure, say 'help me' or 'exit'."
		should_end_session = False
		
	card_title = "Welcome"
	
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))


def reset_response(session):
	""" If we wanted to initialize the session to have some attributes we could
	add those here
	"""
	#print ("* reset_response")
	
	"""
	Reloading Sensibo info to session attributes
	"""
	client = SensiboClientAPI(my_api_key)
	pod_uids = client.pod_uids()
	last_ac_state = client.pod_ac_state(pod_uids[0])
	currMsr = client.pod_measurement(pod_uids[0])
	
	if last_ac_state['acState']['on'] :
		my_last_ac_state = "on"
	else:
		my_last_ac_state = "off"
		
	if last_ac_state['acState']['temperatureUnit'] == 'C' :
		my_temp_type = "Celsius"
	else:
		my_temp_type = "Fahrenheit"
		
	session_attributes = create_current_action_attributes(last_ac_state['acState']['mode'],	last_ac_state['acState']['targetTemperature'],last_ac_state['acState']['fanLevel'],currMsr[0]['temperature'],currMsr[0]['humidity'],my_last_ac_state,my_temp_type)
	
	speech_output = "Measurements and settings were reset." 
	# If the user either does not reply to the welcome message or says something
	# that is not understood, they will be prompted again with this text.
	reprompt_text = "Please let me know what you want me to do, " \
						"If you are unsure, say 'help me' or 'exit'."
	should_end_session = False
		
	card_title = "Reset measurements"
	
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

		
def set_temp_in_session(intent, session):
	""" Sets the temperature in the session and prepares the speech to reply to the
	user.
	"""
	#print ("* set_temp_in_session")

	card_title = "Set Temperature"
	session_attributes = session.get('attributes', {})
	should_end_session = False

	#print("**T**")
	#print(session_attributes)
	#print(intent['slots'])
	#print("****")
	#PreviousTemp = session_attributes['requested_temperature']
	
	if 'value' in intent['slots']['Temperature']:
		""" App is designed for Celsius at the moment, bur should be easy to convert to Fahrenheit in the code...."""
		if (int(intent['slots']['Temperature']['value']) >= 16) or (int(intent['slots']['Temperature']['value']) <= 30):
			requested_temperature = intent['slots']['Temperature']['value']
			session_attributes['requested_temperature'] = intent['slots']['Temperature']['value']
			
			speech_output = "Temperature set to: " + \
							requested_temperature + \
							"."		
			reprompt_text = "What would you like to do next?" \
							"If you are unsure, say 'help me' or 'exit'."
		else:
			speech_output = "I am sorry, I can not update the settings - Temperature can only be set between 16 and 30 degrees Celsius."			
			reprompt_text = "What would you like to do next?" \
							"If you are unsure, say 'help me' or 'exit'."			
	else:
		speech_output = "I'm not sure what you wanted me to do. " \
						"Please try again."
		reprompt_text = "I'm not sure what you wanted me to do. " \
						"If you are unsure, say 'help me' or 'exit'."
	
	#print("**After**")
	#print(session_attributes)
	#print("****")
		
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

	
def set_mode_in_session(intent, session):
	""" Sets the mode in the session and prepares the speech to reply to the
	user.
	"""
	#print ("* set_mode_in_session")

	card_title = "Set AC Mode"
	session_attributes = session.get('attributes', {})
	should_end_session = False

	#print("**M**")
	#print(session_attributes)
	#print(intent['slots'])
	#print("****")
	#PreviousMode = session_attributes['requested_mode']
	
	if 'value' in intent['slots']['ModeType']:
		requested_mode = intent['slots']['ModeType']['value']
		session_attributes['requested_mode'] = intent['slots']['ModeType']['value']
		speech_output = "Mode set to: " + \
						requested_mode + \
						"."		
		reprompt_text = "What would you like to do next?" \
						"If you are unsure, say 'help me' or 'exit'."
	else:
		speech_output = "I'm not sure what you wanted me to do. " \
						"Please try again."
		reprompt_text = "I'm not sure what you wanted me to do. " \
						"If you are unsure, say 'help me' or 'exit'."
	
	#print("**After**")
	#print(session_attributes)
	#print("****")
		
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

	
def set_fan_in_session(intent, session):
	""" Sets the mode in the session and prepares the speech to reply to the
	user.
	"""
	#print ("* set_fan_in_session")

	card_title = "Set Fan Speed"
	session_attributes = session.get('attributes', {})
	should_end_session = False

	#print("**F**")
	#print(session_attributes)
	#print(intent['slots'])
	#print("****")
	#PreviousFanSpeed = session_attributes['requested_fan_speed']
	
	possible_fan_speeds = ["low","medium","high","auto"]
	
	if 'value' in intent['slots']['FanSpeed']:
		possible_word_fix_for_hight = ["high","hi","height","hight","hide"]
		""" Since some times Alexa hears wrong - common variations to high """
		if (intent['slots']['FanSpeed']['value']) in possible_word_fix_for_hight:
			print ("*** fixing to high")
			intent['slots']['FanSpeed']['value'] = "high"
		""" verify setting is acceptable (otherwise skip the action in the else) """
		if (intent['slots']['FanSpeed']['value']) in possible_fan_speeds:
			requested_fan_speed = intent['slots']['FanSpeed']['value']
			session_attributes['requested_fan_speed'] = intent['slots']['FanSpeed']['value']
			
			speech_output = "Requested fan set to: " + \
							requested_fan_speed + \
							"."		

			reprompt_text = "What would you like to do next?" \
							"If you are unsure, say 'help me' or 'exit'."
		else:
			speech_output = "I'm not sure what you wanted me to do. " \
							"Please try again."
			reprompt_text = "I'm not sure what you wanted me to do. " \
							"If you are unsure, say 'help me' or 'exit'."

	else:
		speech_output = "I'm not sure what you wanted me to do. " \
						"Please try again."
		reprompt_text = "I'm not sure what you wanted me to do. " \
						"If you are unsure, say 'help me' or 'exit'."
	
	#print("**After**")
	#print(session_attributes)
	#print("****")
		
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

	
def set_all_in_session(intent, session):
	""" Sets mode, temperature and fan speed in the session and prepares the speech to reply to the
	user.
	"""
	#print ("* set_all_in_session")

	card_title = "Set All AC Settings"
	session_attributes = session.get('attributes', {})
	should_end_session = False

	print("**A**")
	print(session_attributes)
	print(intent['slots'])
	print("****")
	
	possible_fan_speeds = ["low","medium","high","auto"]
		
	if 'value' in intent['slots']['ModeType'] and 'value' in intent['slots']['Temperature']:
		requested_mode = intent['slots']['ModeType']['value']
		requested_Temperature = intent['slots']['Temperature']['value']
		session_attributes['requested_mode'] = intent['slots']['ModeType']['value']
		session_attributes['requested_temperature'] = intent['slots']['Temperature']['value']

		""" in case the user did not provide fan speed or it's invalid, keep the current one """
		if 'value' in intent['slots']['FanSpeed']:
			possible_word_fix_for_hight = ["high","hi","height","hight","hide"]
			""" Since some times Alexa hears wrong - common variations to high """
			if (intent['slots']['FanSpeed']['value']) in possible_word_fix_for_hight:
				print ("*** fixing to high")
				intent['slots']['FanSpeed']['value'] = "high"
			""" verify setting is acceptable (otherwise keep current speed in the else) """
			if (intent['slots']['FanSpeed']['value']) in possible_fan_speeds:	
				requested_fan_speed = intent['slots']['FanSpeed']['value']
				session_attributes['requested_fan_speed'] = intent['slots']['FanSpeed']['value']
			else:
				requested_fan_speed = "Same as it was"	
		else:
			requested_fan_speed = "Same as it was"

				
		speech_output = "As requested, mode set to: " + \
						requested_mode + \
						", Temperature updated to: " + \
						requested_Temperature + \
						", fan to:" + \
						requested_fan_speed + \
						"."
		reprompt_text = "Please let me know what you want me to do by saying. " \
						"If you are unsure, say 'help me' or 'exit'."
	else:
		speech_output = "I'm not sure what you wanted me to do. " \
						"Please try again."
		reprompt_text = "I'm not sure what you wanted me to do. " \
						"If you are unsure, say 'help me' or 'exit'."
		
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))


def set_inc_temp_in_session(intent, session):
	""" Sets the temperature in the session and prepares the speech to reply to the
	user.
	"""
	#print ("* set_inc_temp_in_session")

	card_title = "Increase Temperature"
	session_attributes = session.get('attributes', {})
	should_end_session = False

	#print("**IT**")
	#print(session_attributes)
	#print(intent['slots'])
	#print (session_attributes['requested_temperature'])
	#print("****")
	#PreviousTemp = session_attributes['requested_temperature']
	
	#new_temperature = int(session_attributes['requested_temperature']) + 1
	#session_attributes['requested_temperature'] = str (new_temperature)
	
	""" calculate new temp """
	if 'value' in intent['slots']['IncDecBy']:
		new_temperature = int(session_attributes['requested_temperature']) + int (intent['slots']['IncDecBy']['value'])
	else:
		new_temperature = int(session_attributes['requested_temperature']) + 1
	
	""" update settings on if within acceptable range for Celsius """
	if new_temperature <= 30:
		session_attributes['requested_temperature'] = str (new_temperature)
		speech_output = "Requested temperature updated to: " + \
						str(new_temperature) + \
						"."
		reprompt_text = "What would you like me to do next?"
	else:
		speech_output = "Temperature must not be set over 30, currently at: " + \
						session_attributes['requested_temperature'] + \
						"."
		reprompt_text = "I think you asked to increase the temperature but that was not possible, What would you like me to do next?"
		
	#print (session_attributes['requested_temperature'])
	#print("****")

	#print("**After**")
	#print(session_attributes)
	#print("****")
		
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

	
def set_dec_temp_in_session(intent, session):
	""" Sets the temperature in the session and prepares the speech to reply to the
	user.
	"""
	#print ("* set_dec_temp_in_session")

	card_title = "Decrease Temperature"
	session_attributes = session.get('attributes', {})
	should_end_session = False

	#print("**IT**")
	#print(session_attributes)
	#print(intent['slots'])
	#print (session_attributes['requested_temperature'])
	#print("****")
	#PreviousTemp = session_attributes['requested_temperature']
	
	#new_temperature = int(session_attributes['requested_temperature']) + 1
	#session_attributes['requested_temperature'] = str (new_temperature)
	
	""" calculate new temp """
	if 'value' in intent['slots']['IncDecBy']:
		new_temperature = int(session_attributes['requested_temperature']) - int (intent['slots']['IncDecBy']['value'])
	else:
		new_temperature = int(session_attributes['requested_temperature']) - 1
	
	""" update settings on if within acceptable range for Celsius """
	if new_temperature >= 16:
		session_attributes['requested_temperature'] = str (new_temperature)
		speech_output = "Requested temperature updated to: " + \
						str(new_temperature) + \
						"."
		reprompt_text = "What would you like me to do next?"
	else:
		speech_output = "Temperature must not be set under 16, currently at: " + \
						session_attributes['requested_temperature'] + \
						"."
		reprompt_text = "I think you asked to decrease the temperature but that was not possible, What would you like me to do next?"
		
	#print (session_attributes['requested_temperature'])
	#print("****")

	#print("**After**")
	#print(session_attributes)
	#print("****")
		
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))
	
	
def create_current_action_attributes(requested_mode,requested_temperature,requested_fan_speed,current_temperature,current_humidity,my_last_ac_state,my_temp_type):
	return {"requested_mode": requested_mode,
		"requested_temperature": str(requested_temperature),
		"requested_fan_speed": requested_fan_speed,
		"current_temperature": str(current_temperature),
		"current_humidity": str(current_humidity),
		"my_last_ac_state": my_last_ac_state,
		"my_temp_type": my_temp_type}

		
def get_requested_mode_from_session (session):

	requested_mode = "unknown"
	if "requested_mode" in session.get('attributes', {}):
		requested_mode = session['attributes']['requested_mode']
		
	return {requested_mode}

	
def get_requested_temperature_from_session (session):
	
	requested_temperature = "unknown"
	if "requested_temperature" in session.get('attributes', {}):
		requested_temperature = session['attributes']['requested_temperature']
		
	return {requested_temperature}

	
def get_requested_fan_speed_from_session (session):
		
	requested_fan_speed = "unknown"
	if "requested_fan_speed" in session.get('attributes', {}):
		requested_fan_speed = session['attributes']['requested_fan_speed']
	
	return {requested_fan_speed}

	
def get_current_temperature_from_session (session):
	
	current_temperature = "unknown"
	if "current_temperature" in session.get('attributes', {}):
		current_temperature = session['attributes']['current_temperature']
		
	return {current_temperature}

	
def get_current_humidity_from_session (session):

	current_humidity = "unknown"
	if "current_humidity" in session.get('attributes', {}):
		current_humidity = session['attributes']['current_humidity']
					
	return {current_humidity}
	
	
def get_my_last_ac_state_from_session (session):

	my_last_ac_state = "unknown"
	if "my_last_ac_state" in session.get('attributes', {}):
		my_last_ac_state = session['attributes']['my_last_ac_state']
				
	return {my_last_ac_state}
	
	
def get_my_temp_type_from_session (session):

	my_temp_type = "unknown"
	if "my_temp_type" in session.get('attributes', {}):
		my_temp_type = session['attributes']['my_temp_type']
				
	return {my_temp_type}


def get_full_status_from_session(intent, session):
	#print ("* get_full_status_from_session")

	card_title = "Get Settings & Status"
	reprompt_text = None
	session_attributes = session.get('attributes', {})

	""" setting up nice wording for the speech, that's all """
	if get_requested_mode_from_session(session).pop() == "cool" :
		my_mode = "Cooling"
	else:
		my_mode = "Heating"
	
	speech_output = "AC is: " + \
		get_my_last_ac_state_from_session(session).pop() + \
		". Temperature set to: " + \
		get_requested_temperature_from_session(session).pop() + \
		", " + \
		get_my_temp_type_from_session(session).pop() + \
		". mode: " + \
		my_mode + \
		". Fan set to: " + \
		get_requested_fan_speed_from_session(session).pop() + \
		". It is now: " + \
		get_current_temperature_from_session(session).pop() + \
		" " + \
		get_my_temp_type_from_session(session).pop() + \
		", humidity is: " + \
		get_current_humidity_from_session(session).pop() + \
		"."
		
	#print (speech_output)
	should_end_session = False

	# Setting reprompt_text to None signifies that we do not want to reprompt
	# the user. If the user does not respond or says something that is not
	# understood, the session will end.
	return build_response(session_attributes, build_speechlet_response(
		intent['name'], speech_output, reprompt_text, should_end_session))

		
def get_room_status_from_session(intent, session):
	#print ("* get_room_status_from_session")

	card_title = "Get Home Status"
	reprompt_text = None
	session_attributes = session.get('attributes', {})

	speech_output = "It is: " + \
		get_current_temperature_from_session(session).pop() + \
		" " + \
		get_my_temp_type_from_session(session).pop() + \
		", humidity is: " + \
		get_current_humidity_from_session(session).pop() + \
		"."
		
	#print (speech_output)
	should_end_session = False

	# Setting reprompt_text to None signifies that we do not want to reprompt
	# the user. If the user does not respond or says something that is not
	# understood, the session will end.
	return build_response(session_attributes, build_speechlet_response(
		intent['name'], speech_output, reprompt_text, should_end_session))


def get_settings_status_from_session(intent, session):
	#print ("* get_settings_status_from_session")

	card_title = "Get Settings"
	reprompt_text = None
	session_attributes = session.get('attributes', {})
	#print("**ST**")
	#print(session_attributes)
	#print (get_requested_mode_from_session(session).pop())

	""" setting up nice wording for the speech, that's all """
	if get_requested_mode_from_session(session).pop() == "cool" :
		my_mode = "Cooling"
	else:
		my_mode = "Heating"
		
	#print (my_mode)
	#print("****")

	speech_output = "AC is: " + \
		get_my_last_ac_state_from_session(session).pop() + \
		". Temperature set to: " + \
		get_requested_temperature_from_session(session).pop() + \
		", " + \
		get_my_temp_type_from_session(session).pop() + \
		". mode: " + \
		my_mode + \
		". Fan set to: " + \
		get_requested_fan_speed_from_session(session).pop() + \
		"."
	
	#print (speech_output)
	should_end_session = False

	# Setting reprompt_text to None signifies that we do not want to reprompt
	# the user. If the user does not respond or says something that is not
	# understood, the session will end.
	return build_response(session_attributes, build_speechlet_response(
		intent['name'], speech_output, reprompt_text, should_end_session))

		
def set_turnon(intent, session):

	#print ("* set_turnon")
	card_title = "Turn On AC"
	session_attributes = session.get('attributes', {})
	#print (session_attributes['my_last_ac_state'])
	#print("**TO**")
	#print(session_attributes)
	
	client = SensiboClientAPI(my_api_key)
	pod_uids = client.pod_uids()
	#print (pod_uids[0])
	""" sending action """
	client.pod_change_ac_state((pod_uids[0]), True, int(session_attributes['requested_temperature']), str(session_attributes['requested_mode']), str(session_attributes['requested_fan_speed']))
	speech_output = "Command sent to turn on the AC"
	reprompt_text = None
	
	should_end_session = False

	# Setting reprompt_text to None signifies that we do not want to reprompt
	# the user. If the user does not respond or says something that is not
	# understood, the session will end.
	return build_response(session_attributes, build_speechlet_response(
		intent['name'], speech_output, reprompt_text, should_end_session))
		
		
def set_shutdown(intent, session):

	#print ("* set_shutdown")
	card_title = "Turn Off AC"
	session_attributes = session.get('attributes', {})
	#print (session_attributes['my_last_ac_state'])
	print("**SD**")
	print(session_attributes)
	
	client = SensiboClientAPI(my_api_key)
	pod_uids = client.pod_uids()
	#print (pod_uids[0])
	""" sending action """
	client.pod_change_ac_state((pod_uids[0]), False, int(session_attributes['requested_temperature']), str(session_attributes['requested_mode']), str(session_attributes['requested_fan_speed']))
	speech_output = "Command sent turn the AC OFF"
	reprompt_text = None
	
	should_end_session = False

	# Setting reprompt_text to None signifies that we do not want to reprompt
	# the user. If the user does not respond or says something that is not
	# understood, the session will end.
	return build_response(session_attributes, build_speechlet_response(
		intent['name'], speech_output, reprompt_text, should_end_session))		


def get_help(intent, session):
	""" Help texts guiding the user on possible commands """
	#print ("* get_help")

	card_title = "Sensibo App Help"
	session_attributes = session.get('attributes', {})
	should_end_session = False

	#print("**T**")
	#print(session_attributes)
	#print(intent['slots'])
	#print("****")
	#PreviousTemp = session_attributes['requested_temperature']
	
	if 'value' in intent['slots']['helpType']:
		""" Help text for available information commands """
		if (intent['slots']['helpType']['value'] == "information"):
			speech_output = "For information you can say: " + \
							"'Status'; for room temperature and humidity, or 'Settings Status'; for current AC settings. " + \
							"you can also say 'Full status'; for both room measurements and current AC settings."		
			reprompt_text = "What would you like to do next?" \
							"If you are unsure, say 'help me' or 'exit'."
		elif (intent['slots']['helpType']['value'] == "settings"):
			""" Help text for available setting modifications commands """
			speech_output = "For updating AC settings you can say: " + \
							"'set mode to'; followed by either 'cool' or 'heat'. " + \
							"'set fan to'; followed by either 'low', 'medium', 'high' or 'auto'. " + \
							"'set temp to'; followed by a number between 16 and 30 Celsius. " + \
							"you can also say 'Increase' or 'decrease temperature by'; followed by 1, 2 or more..."		
			reprompt_text = "What would you like to do next?" \
							"If you are unsure, say 'help me' or 'exit'."
		elif (intent['slots']['helpType']['value'] == "actions"):
			""" Help text for available actions that communicate with Sensibo web service """
			speech_output = "You can say 'turn on'; in order to activate the AC with current settings, " + \
							"You can say 'shut down'; to stop the AC, " + \
							"or, you can say 'Reset'; to retake AC measurements and reset the settings"
			reprompt_text = "What would you like to do next?" \
							"If you are unsure, say 'help me' or 'exit'."
		else:
			"""" Help text on the possible help topics """
			speech_output = "There are three help topics, say 'help me with information' or 'settings' or 'actions'," \
							"depending on what you want to do."
			reprompt_text = "I'm not sure what you wanted me to do. " \
							"please say 'help me with', followed by the topic - 'Information', 'Settings' or 'Actions'."
	else:
		speech_output = "There are three help topics, say 'help me with information' or 'settings' or 'actions'," \
						"depending on what you want to do."
		reprompt_text = "I'm not sure what you wanted me to do. " \
						"please say 'help me with', followed by the topic - 'Information', 'Settings' or 'Actions'."
	
	#print("**After**")
	#print(session_attributes)
	#print("****")
		
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

		
# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Sensibo Voice - ' + title,
            'content': 'Sensibo - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
	return {
		'version': '1.0',
		'sessionAttributes': session_attributes,
		'response': speechlet_response
	}