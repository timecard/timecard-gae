import endpoints

_allowed_client_ids = [
  endpoints.API_EXPLORER_CLIENT_ID,
  "636938638718.apps.googleusercontent.com", # web application
  "636938638718-f7fose4kkhe2imf1c38l25fsamarn8ei.apps.googleusercontent.com", # Chrome application
  "636938638718-q1shs6aa5rnflil339rhset2rs9fcq52.apps.googleusercontent.com", # iOS application
]

api = endpoints.api(name="timecard", version="dev",
                    description = "timecard API",
                    allowed_client_ids = _allowed_client_ids,
                   )

api_services = [api]
