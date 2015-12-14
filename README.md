# Sensibo Skill for Amazon Echo (Alexa)

** coded using Alexa Skill Kit sample by Amazon & Sensibo API **
** by Amir Hanan **

Use / modify as you wish - ** for private use only **

### What you will need

	- Basic understanding of python / coding skills
	- Recommended reading: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/getting-started-guide
	- Access to Amazon developer's portal https://developer.amazon.com/appsandservices
	- Access to Amazon Web Services (AWS) https://aws.amazon.com/
	- Access to Sensibo web app where you will get your API key https://home.sensibo.com/me/api
	
	
### Installation Instructions

	** Getting the code ready **
	
	- Download the content of this git to a local folder
	- Edit lambda_function.py
		update your API key to 'my_api_key' (line 17) should look like that

```sh
		my_api_key = 'some long string of letters & digits...'
```

	- Zip only the following inside this folder (not the entire containing folder)
		the file: lambda_function.py
		The sub folder: requests
		
	** Creating the Lambda function **
	
	- Open Lamnda section in AWS https://console.aws.amazon.com/lambda/
	- Make sure you are using east USA location (top right selection near your profile name)
	- Click "Create a Lambda function"
	- Click "Skip"
	- Write the name of your function and a description as you wish
		(I called it "Sensibo Voice")
	- Choose "Python 2.7 " in "Runtime"
	- Create a new "Basic Execution Role"
	- Under "Advanced settings", update "Timeout" to 7 seconds
	- Click "Next", review and click "Create function" once you are satisfied.
	
	- Under the "Code" tab, choose "Upload a ZIP file" and upload the ZIP you created per above instructions.
	- Copy the ARN code for this function (from the top right)
	
		should look something like this:
			arn:aws:lambda:us-east-1:3423432:function:functionname
	
	** Setting app the skill **
	
	- In "Amazon developer portal" choose "Apps & Services" and under that "Alexa"
	- Click "Get Started" for "Alexa Skills Kit", than "Add a New Skill"
	- Give the skill a name as you see fit (I'm using SensiboVoice)
	- Set "Invocation Name" - this will be the word that tells Alexa to activate the skill (I'm using "Sensibo")
		so I'll say for example "Alexa open Sensibo"
	- Set "Version" (1.0)
	- In "Endpoint" choose ARN and paste the code you saved above
	- Copy the content from the file "INTENT_SCHEMA.txt" (in your local git folder) to "Intent Schema"
	- Add "Custom Slot Types"
		HELP_TYPES with the content from HELP_TYPES.txt
		INC_BY_OPTIONS with the content from INC_BY_OPTIONS.txt
		LIST_OF_FANSPEED with the content from LIST_OF_FANSPEED.txt
		LIST_OF_MODE_TYPES with the content from LIST_OF_MODE_TYPES.txt
		LIST_OF_TEMP with the content from LIST_OF_TEMP.txt
		
		All relevant files for content should be in your local git file, just copy and paste the type per file name and the values from the content)

	- Copy & paste "Sample Utterances" from SAMPLE_UTTERANCES.txt
	- Click "Next"
	- Make sure the function is "enabled" for testing
	
	** At this point the app can only by used by an Amazon Echo which is resisted to the same user as the Amazon developers portal! **
	** Note this code is intended for personal use only and not for public installation / release of official skill!
	
	### What's next?
	
		If you followed all the above and nothing went wrong, you should be able to control your Sensibo using you Amazon echo...
		
	Contact me for question / problems via email.
	