from app import app

# Vercel serverless function entry point
def handler(request, response):
    return app(request.environ, response.start_response)

# For Vercel
application = app
