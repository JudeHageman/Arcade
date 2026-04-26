# client/main.py
from arcade_app import ArcadeApp

def main():
    app = ArcadeApp()
    
    # 임시: 첫 화면 설정 로직이 들어갈 곳
    # app.switch_screen("LOGIN") 
    
    app.run()

if __name__ == "__main__":
    main()