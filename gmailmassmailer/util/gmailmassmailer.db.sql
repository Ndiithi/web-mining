BEGIN TRANSACTION;
CREATE TABLE "recipient" (
	`email`	TEXT,
	`campaign`	INTEGER,
	PRIMARY KEY(`email`,`campaign`),
	FOREIGN KEY(`campaign`) REFERENCES `campaign`(`campaign_id`) ON DELETE CASCADE ON UPDATE NO ACTION
);
CREATE TABLE error ( error_id INTEGER, detail TEXT(200),
            time_created TEXT(100),  PRIMARY KEY(error_id) );
INSERT INTO `error` (error_id,detail,time_created) VALUES (1,'Could not log in to gmail for account user: duncanndiithi password: elizabeth@wairimu26 please see error image at /home/duncan/workspace/GmailMassMailer/gmailmassmailer/service/logs/duncanndiithi_login_error.png
Message: no such element: Unable to locate element: {"method":"xpath","selector":"//input[@name="identifier"]"}
  (Session info: chrome=62.0.3202.94)
  (Driver info: chromedriver=2.32.498513 (2c63aa53b2c658de596ed550eb5267ec5967b351),platform=Linux 4.11.12-100.fc24.x86_64 x86_64)
','2018/02/16 13:08:16'),
 (2,'Could not log in to gmail for account user: duncanndiithi password: elizabeth@wairimu26 please see error image at /home/duncan/workspace/GmailMassMailer/gmailmassmailer/service/logs/duncanndiithi_login_error.png
Message: no such element: Unable to locate element: {"method":"xpath","selector":"//input[@name="identifier"]"}
  (Session info: chrome=62.0.3202.94)
  (Driver info: chromedriver=2.32.498513 (2c63aa53b2c658de596ed550eb5267ec5967b351),platform=Linux 4.11.12-100.fc24.x86_64 x86_64)
','2018/02/16 13:14:23'),
 (3,'Could not log in to gmail for account user: duncanndiithi password: elizabeth@wairimu26 please see error image at /home/duncan/workspace/GmailMassMailer/gmailmassmailer/service/logs/duncanndiithi_login_error.png
Message: no such element: Unable to locate element: {"method":"xpath","selector":"//input[@name="identifier"]"}
  (Session info: chrome=62.0.3202.94)
  (Driver info: chromedriver=2.32.498513 (2c63aa53b2c658de596ed550eb5267ec5967b351),platform=Linux 4.11.12-100.fc24.x86_64 x86_64)
','2018/02/16 13:16:48'),
 (4,'Could not log in to gmail for account user: duncanndiithi password: elizabeth@wairimu26 please see error image at /home/duncan/workspace/GmailMassMailer/gmailmassmailer/service/logs/duncanndiithi_login_error.png
Message: no such element: Unable to locate element: {"method":"xpath","selector":"//input[@name="identifier"]"}
  (Session info: chrome=62.0.3202.94)
  (Driver info: chromedriver=2.32.498513 (2c63aa53b2c658de596ed550eb5267ec5967b351),platform=Linux 4.11.12-100.fc24.x86_64 x86_64)
','2018/02/16 13:23:01'),
 (5,'Could not log in to gmail for account user: duncanndiithi password: elizabeth@wairimu26 please see error image at /home/duncan/workspace/GmailMassMailer/gmailmassmailer/service/logs/duncanndiithi_login_error.png
Message: no such element: Unable to locate element: {"method":"xpath","selector":"//input[@name="identifier"]"}
  (Session info: chrome=62.0.3202.94)
  (Driver info: chromedriver=2.32.498513 (2c63aa53b2c658de596ed550eb5267ec5967b351),platform=Linux 4.11.12-100.fc24.x86_64 x86_64)
','2018/02/16 13:23:36'),
 (6,'Could not log in to gmail for account user: duncanndiithi password: elizabeth@wairimu26 please see error image at /home/duncan/workspace/GmailMassMailer/gmailmassmailer/service/logs/duncanndiithi_login_error.png
Message: no such element: Unable to locate element: {"method":"xpath","selector":"//input[@name="identifier"]"}
  (Session info: chrome=62.0.3202.94)
  (Driver info: chromedriver=2.32.498513 (2c63aa53b2c658de596ed550eb5267ec5967b351),platform=Linux 4.11.12-100.fc24.x86_64 x86_64)
','2018/02/16 18:43:58'),
 (7,'Could not log in to gmail for account user: duncanndiithi password: elizabeth@wairimu26 please see error image at /home/duncan/workspace/GmailMassMailer/gmailmassmailer/service/logs/duncanndiithi_login_error.png
Message: no such element: Unable to locate element: {"method":"xpath","selector":"//input[@name="identifier"]"}
  (Session info: chrome=62.0.3202.94)
  (Driver info: chromedriver=2.32.498513 (2c63aa53b2c658de596ed550eb5267ec5967b351),platform=Linux 4.11.12-100.fc24.x86_64 x86_64)
','2018/02/16 18:44:35'),
 (8,'Failed to read accounts list file 
list index out of range','2018/02/25 19:14:00'),
 (9,'Failed to read accounts list file 
__init__() takes at least 3 arguments (1 given)','2018/02/25 19:21:36'),
 (10,'Failed to read accounts list file 
list index out of range','2018/02/25 19:23:40'),
 (11,'Failed to read accounts list file 
list index out of range','2018/02/25 19:24:48'),
 (12,'Failed to read accounts list file 
list index out of range','2018/02/25 19:25:08'),
 (13,'Error during mail composition for account user: duncanndiithi@gmail.com please see error image at /home/duncan/workspace/GmailMassMailer/gmailmassmailer/view/logs/duncanndiithi@gmail.commail_compose_error.png
Message: element not visible
  (Session info: chrome=64.0.3282.167)
  (Driver info: chromedriver=2.32.498513 (2c63aa53b2c658de596ed550eb5267ec5967b351),platform=Linux 4.14.18-200.fc26.x86_64 x86_64)
','2018/02/25 20:57:59'),
 (14,'Failed to read recipients list file 
coercing to Unicode: need string or buffer, list found','2018/02/26 00:35:37'),
 (15,'Failed to read accounts list file 
coercing to Unicode: need string or buffer, list found','2018/02/26 00:35:37'),
 (16,'Failed to read recipients list file 
coercing to Unicode: need string or buffer, list found','2018/02/26 00:38:21'),
 (17,'Failed to read accounts list file 
coercing to Unicode: need string or buffer, list found','2018/02/26 00:38:21');
CREATE TABLE "Message" (
	`message_id`	INTEGER,
	`text`	TEXT,
	`campaign`	INTEGER,
	FOREIGN KEY(`campaign`) REFERENCES `campaign`(`campaign_id`) ON DELETE CASCADE ON UPDATE NO ACTION
);
CREATE TABLE "Campaign" (
	`campaign_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`Date`	TEXT
);
CREATE TABLE "Account" (
	`account_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`user_name`	TEXT,
	`password`	TEXT,
	`total_sent`	INTEGER,
	`campaign`	INTEGER,
	FOREIGN KEY(`campaign`) REFERENCES `campaign`(`campaign_id`) ON DELETE CASCADE ON UPDATE NO ACTION
);
COMMIT;
