from flask import Flask, render_template,redirect,request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Create_db import User, Video, Likes, Subscribe, Comments
import os
import ffmpeg

def make_preview(video_path, output_image_path):
    preview_dir = os.path.join('static', 'previews')
    
    full_output_path = os.path.join(preview_dir, output_image_path)
    
    ffmpeg.input(video_path, ss=1).output(full_output_path, vframes=1, s='640x360').run(cmd='D:/ffmpeg/ffmpeg-7.1-essentials_build/bin/ffmpeg.exe')

engine = create_engine('sqlite:///Data_Base.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)

@app.route('/registration')
def registration():
    return render_template('Registration.html')

@app.route('/register', methods=['POST'])
def register():
    
    User_email = request.form['email']

    
    existing_user = session.query(User).filter_by(login=User_email).first()
    if existing_user:
        return 'Такий користувач вже існує'

    
    User_password = request.form['password']
    New_user = User(login=User_email, password=User_password)
    session.add(New_user)
    session.commit()

    return redirect(f'/home/{New_user.id}')


@app.route('/home/<user_id>')
def home(user_id):
    avatar_exists = os.path.exists(f"static/Avatar/avatar_{user_id}.jpg")
    videos_names=session.query(Video).all()
    Users = session.query(User).all()
    return render_template('Home.html',user_id_=user_id,video_names=videos_names, Users=Users,avatar_exists=avatar_exists)

@app.route('/Enter')
def Enter():
    return render_template('Enter.html')

@app.route('/check', methods=['POST'])
def Check_person():
    Check_login = request.form['email']
    Check_password = request.form['password']
    existing_user = session.query(User).filter_by(login=Check_login).first()
    if existing_user:
                if existing_user.password == Check_password:
                    return redirect(f'/home/{existing_user.id}')
                else:
                    return 'Невірний пароль'
    else:
        return 'Невірний Імейл'


@app.route('/main/<int:user_id>')
def main(user_id):
    user = session.query(User).filter_by(id=user_id).first()  
    videos_names=session.query(Video).filter_by(user_id=user_id).all()
    if user:  
        return render_template('Main.html', user=user, user_id_=user_id,videos_names=videos_names) 
    return redirect('/Enter') 


@app.route('/new_video/<int:user_id>')
def new_video(user_id):
     return render_template('new_video.html', user_id_=user_id)


@app.route('/upload/<int:user_id>', methods=['POST'])
def upload(user_id):
    File = request.files['video']
    Video_name = request.form['video_name']
    User_preview=request.files['preview']
    
    
    Add_video = Video(filename=Video_name, user_id=user_id)
    session.add(Add_video)
    session.commit()


    New_name = f'video_{Add_video.id}.mp4'
    File.save(os.path.join('static/Save_folder', New_name))
    
    Add_name = session.query(Video).filter_by(id = Add_video.id).first()
    Add_name.new_filename=New_name
    session.commit()
    if User_preview.filename=='':
         make_preview (f'static/Save_folder/{New_name}', f'preview_{Add_video.id}.jpg')
    else:
         User_preview.save(os.path.join('static/Previews',f'preview_{Add_video.id}.jpg'))
    preview=session.query(Video).filter_by(id = Add_video.id).first()
    preview.preview=True
    return redirect(f'/home/{user_id}')

@app.route('/video/<int:video_id>/<int:user_id>')
def Videos(video_id,user_id):
    avatar_exists = os.path.exists(f"static/Avatar/avatar_{user_id}.jpg")
    videos_names=session.query(Video).all()
    Users = session.query(User).all()
    video = session.query(Video).filter_by(id=video_id).first()
    subscribed = session.query(Subscribe).filter_by(user_id=user_id,author_id=video.user_id).first()
    liked = session.query(Likes).filter_by(user_id=user_id,video_id=video_id).first()
    if not video:
        return "Video not found", 404
    watch_video = f'/static/Save_folder/video_{video.id}.mp4'
    comments=session.query(Comments).all()
    like_amount=0
    likes=session.query(Likes).filter_by(video_id=video_id).all()
    for like in likes:
        like_amount+=1
    subscribe_amount=0
    subscribes=session.query(Subscribe).filter_by(author_id=video.user_id).all()
    for subscribe in likes:
        subscribe_amount+=1
    return render_template('Video.html', watch_video=watch_video,video_name=video,user_id_=user_id,
    avatar_exists=avatar_exists,Users=Users,subscribed=subscribed,liked=liked,comments=comments,videos_names=videos_names,
    video_id=video_id,like_amount=like_amount,subscribe_amount=subscribe_amount)

     
@app.route('/edit_channel/<int:user_id>')
def edit_channel(user_id):
     return render_template('edit_channel.html', user_id_=user_id)


@app.route('/sumbit_edits/<int:user_id>', methods=['POST'])
def sumbit_edits(user_id):
    New_avatar=request.files['avatar']
    New_nickname=request.form['new_nickname']
    user=session.query(User).filter_by(id=user_id).first()
    if New_nickname !='':
        user.nickname=New_nickname
        session.commit()
    if New_avatar.filename != '':
        avatar_path = os.path.join('static/Avatar', f'avatar_{user_id}.jpg')

        if os.path.exists(avatar_path):
            os.remove(avatar_path)
            user.avatar = False
        New_avatar.save(avatar_path)
        user.avatar = True
        session.commit()
    return redirect(f'/home/{user_id}')


@app.route('/subscribe/<int:user_id>/<int:author_id>/<int:video_id>')
def subscribe(user_id,author_id,video_id):
    is_subscribed=session.query(Subscribe).filter_by(user_id=user_id, author_id=author_id).first()
    if is_subscribed:
        session.query(Subscribe).filter_by(user_id=user_id, author_id=author_id).delete()
    else:
        new_subscribtion = Subscribe(user_id=user_id,author_id=author_id,subscribed=True)
        session.add(new_subscribtion)
    session.commit()
    return redirect(f'/video/{video_id}/{user_id}')

@app.route('/like/<int:user_id>/<int:video_id>')
def like(user_id,video_id):
    liked=session.query(Likes).filter_by(user_id=user_id, video_id=video_id).first()
    if liked:
        session.query(Likes).filter_by(user_id=user_id, video_id=video_id).delete()
    else:
        new_like = Likes(user_id=user_id,video_id=video_id,is_liked=True)
        session.add(new_like)
    session.commit()
    return redirect(f'/video/{video_id}/{user_id}')

@app.route('/post_comment/<int:user_id>/<int:video_id>', methods=['POST'])
def post_comment(user_id,video_id):
    comment=request.form['comment_text']
    if comment != '':
        add_comment=Comments(user_id=user_id,video_id=video_id,text=comment)
        session.add(add_comment)
        session.commit()
    return redirect(f'/video/{video_id}/{user_id}')

@app.route('/user_page/<int:user_id>/<int:author_id>')
def user_page(user_id,author_id):
    author=session.query(User).filter_by(id=author_id).first()
    videos_names=session.query(Video).filter_by(user_id=author_id).all()
    return render_template('visit_channel.html',user_id=user_id,author_id=author_id,author=author,videos_names=videos_names)

@app.route('/delete/<int:video_id>/<int:user_id>')
def delete_video(video_id,user_id):
    session.query(Video).filter_by(id=video_id).delete()
    session.query(Likes).filter_by(video_id=video_id).delete()
    session.query(Comments).filter_by(video_id=video_id).delete()
    session.commit()

    video_path = f"static/Save_folder/video_{video_id}.mp4"
    if os.path.exists(video_path):
        os.remove(video_path)
        print("Файл видалено")

    photo_path = f"static/Previews/preview_{video_id}.jpg"
    if os.path.exists(photo_path):
        os.remove(photo_path)
        print("Файл видалено")


    return redirect(f'/home/{user_id}')


session.close()

if __name__=="__main__":
    app.run(debug=True)