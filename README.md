$ source venv/bin/activate
$ pip install -r requirements.txt
$ brew install --cask google-cloud-sdk
$ gcloud auth application-default login
Your browser has been opened to visit:

    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8085%2F&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login&state=mTY9n0jxQpcr6z6jhXsBPwkdG2lGwC&access_type=offline&code_challenge=9zAWDMc05uxROAt9gv9mRwkZsGifR9qq4ssqWuJtGQA&code_challenge_method=S256


Credentials saved to file: [/Users/lmizuhashi/.config/gcloud/application_default_credentials.json]

These credentials will be used by any library that requests Application Default Credentials (ADC).
WARNING: 
Cannot find a quota project to add to ADC. You might receive a "quota exceeded" or "API not enabled" error. Run $ gcloud auth application-default set-quota-project to add a quota project.