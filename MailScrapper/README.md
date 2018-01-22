
# MailScrapper

Given an excel sheet of sites, the crawler grabs mails from the sites and saves them side by side to the sites domains.

# Running

step 1:
    
    pip install -r requirements.txt

Step 2:
    
    scrapy crawl MailSrapper
    
# Note

Take caution as you customize this crawler for your own needs, it could potentially slow down a webserver, make it crash or you could get your ip blocked. 

To caution against the above, i have initialiized a few scrapy settings by default:

        USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Galeon/2.0.6 (Ubuntu 2.0.6-2)'
        CONCURRENT_REQUESTS = 10
        DOWNLOAD_DELAY = 3
        AUTOTHROTTLE_ENABLED = True
        AUTOTHROTTLE_TARGET_CONCURRENCY = 5.0
        
You could also enable: COOKIES_ENABLED  setting by setting it to true, however, this can slow down your crwals, but could still help avoiding detection as a bot.
