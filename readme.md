# Temperature blanket data
My Wife is making a temperature blanket and needed to get the daily temperature and its associated color.

This project gets the current weather based on my longitude and latitude and uploads it and the color hex based on the NOAA rainbow temperature palette to a Google sheet via the Google cloud console api. Since I want this to be run once a day I created an image with Docker and uploaded it to AWS ECR and ran the image with Lambda having CloudWatch Events run it once a day at 8am. 

There are a lot of easier ways to accomplish this but I wanted practice using AWS and docker and was a perfect learning experince.
## Tech used
- Docker
- Aws ECR(Elastic Container Registry)
- Aws Lambda
- Aws EventBridge(CloudWatch Events)
- Google Cloud Console - Google Sheets API

![alt text](https://raw.githubusercontent.com/jacobpetersonwastaken/Tempature-Blanket/main/images/Asset%202.png)
