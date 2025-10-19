'''
@author Huy Le (hl9082)
  @co-author Will Stott, Zoe Shearer, Josh Elliot
@purpose
    This script serves as the main entry point for the backend server.
    It starts the FastAPI application using uvicorn.
 @importance
    This file is used to launch the backend services, making them available to
   the frontend.

'''
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)