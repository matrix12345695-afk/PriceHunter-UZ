import os
import uvicorn
from dotenv import load_dotenv
load_dotenv()

def main():
    uvicorn.run('app.web.server:app',host=os.getenv('HOST','0.0.0.0'),port=int(os.getenv('PORT','8000')),workers=1)

if __name__=='__main__':
    main()
