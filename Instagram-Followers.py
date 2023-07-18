import instaloader
import PySimpleGUI as sg
import random
from PIL import ImageTk, Image
from urllib.request import urlopen
import tempfile
import os

# Tema ve stil ayarları
sg.theme("DarkBlue")

# TUA logosu
logo_image = "img/TUA_Logo2.png"

# Kullanıcının profil bilgilerini almak için bir fonksiyon
def get_profile_info(username, password):
    # Yeni bir instaloader örneği oluştur
    L = instaloader.Instaloader()

    # Kullanıcı girişi yapmayı dene, başarısız olursa hata mesajı göster
    try:
        L.login(username, password)
    except instaloader.exceptions.LoginRequiredException:
        sg.popup_error("Hatalı kullanıcı adı veya şifre!")
        return None, None, None, None

    # Verilen kullanıcı adından bir profil oluştur
    profile = instaloader.Profile.from_username(L.context, username)

    # Profilin takipçi, takip edilen, gönderi sayısı ve profil resmini al
    followers_count = profile.followers
    followees_count = profile.followees
    posts_count = profile.mediacount
    profile_pic_url = profile.profile_pic_url

    # Bu bilgileri döndür
    return followers_count, followees_count, posts_count, profile_pic_url

# Kullanıcının takipçi ve takip edilenlerini almak için bir fonksiyon
def get_followers_and_followees(username, password):
    # Yeni bir instaloader örneği oluştur
    L = instaloader.Instaloader()

    # Kullanıcı girişi yapmayı dene, başarısız olursa hata mesajı göster
    try:
        L.login(username, password)
    except instaloader.exceptions.LoginRequiredException:
        sg.popup_error("Hatalı kullanıcı adı veya şifre!")
        return

    # Verilen kullanıcı adından bir profil oluştur
    profile = instaloader.Profile.from_username(L.context, username)

    # Takipçi ve takip edilenlerin kaydedileceği dosya adları
    followers_file = "followers.txt"
    followees_file = "following.txt"

    # Takipçi ve takip edilenleri dosyalara kaydetmeyi dene, başarısız olursa hata mesajı göster
    try:
        with open(followers_file, "w") as f:
            for followers in profile.get_followers():
                f.write(followers.username + '\n')

        with open(followees_file, "w") as f:
            for followees in profile.get_followees():
                f.write(followees.username + '\n')

        sg.popup("Takipçiler ve takip edilenler kaydedildi.")
    except Exception as e:
        sg.popup_error("Bir hata oluştu: " + str(e))

# Kullanıcının takip etmeyenleri bulmak için bir fonksiyon
def find_unfollowers():
    followers_file = "followers.txt"
    followees_file = "following.txt"

    # Takipçi ve takip edilenleri dosyalardan okumayı dene, başarısız olursa hata mesajı göster
    try:
        followers = set(open(followers_file).read().splitlines())
        followees = set(open(followees_file).read().splitlines())

        # Takip etmeyenleri bul
        unfollowers = followees - followers

        # Eğer takip etmeyen yoksa mesaj göster, varsa liste olarak göster
        if len(unfollowers) == 0:
            sg.popup("Takip etmeyen kullanıcı bulunamadı.")
        else:
            result_text = "Takip etmeyenler:\n"
            for unfollower in unfollowers:
                result_text += unfollower + "\n"
            result = sg.popup_ok_cancel(result_text, title="Takip Etme İşlemi", keep_on_top=True)
            if result == "OK":
                # Takipten çıkış işlemi
                try:
                    L = instaloader.Instaloader()
                    L.login(username, password)
                    for unfollower in unfollowers:
                        L.unfollow(unfollower)
                    sg.popup("Takipten çıkıldı!")
                except Exception as e:
                    sg.popup_error("Takipten çıkış sırasında bir hata oluştu: " + str(e))
    except FileNotFoundError:
        sg.popup_error("Takipçi ve takip edilenler dosyaları bulunamadı.")
    except Exception as e:
        sg.popup_error("Bir hata oluştu: " + str(e))

# Profil resmini geçici bir dosyaya kaydeden yardımcı bir fonksiyon
def save_profile_pic(profile_pic_url):
    with urlopen(profile_pic_url) as response:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.read())
            return temp_file.name

# Pencere düzeni
layout = [
    [
        sg.Column(
            [
                [sg.Image(filename=logo_image, size=(300, 300))],
                [sg.Image(key="-PROFILE_PIC-", size=(150, 150))],
                [
                    sg.Text("Kullanıcı Adı:", font=("Helvetica", 12)),
                    sg.Input(key="-USERNAME-", size=(20, 1), font=("Helvetica", 12)),
                    sg.Text("Şifre:", font=("Helvetica", 12)),
                    sg.Input(key="-PASSWORD-", password_char="*", size=(20, 1), font=("Helvetica", 12))
                ],
                [sg.Button("Profil Bilgilerini Göster", size=(25, 1), font=("Helvetica", 12))],
                [sg.Button("Takipçi ve Takip Edilenleri Al", size=(25, 1), font=("Helvetica", 12))],
                [sg.Button("Takip Etmeyenleri Bul", size=(25, 1), font=("Helvetica", 12))],
                [sg.Button("Takip Etmeyenleri Takipten Çık!", size=(25, 1), font=("Helvetica", 12))],
                [sg.Multiline(key="-INFO-", size=(40, 10), font=("Helvetica", 12), disabled=True, autoscroll=True)],
                [sg.Text("TOALEY tarafından tüm hakları saklıdır.", font=("Helvetica", 10), justification="center", pad=(0, 15))]
            ],
            element_justification="center",
            pad=(50, 50)
        )
    ]
]

# Pencere oluşturma
window = sg.Window("TUA Takipçi Analizi Uygulaması", layout, element_justification="center", font=("Helvetica", 12))

# Pencere olayları döngüsü
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Profil Bilgilerini Göster":
        username = values["-USERNAME-"]
        password = values["-PASSWORD-"]
        followers, following, posts, profile_pic_url = get_profile_info(username, password)
        if followers is not None:
            info_text = f"Takipçi Sayısı: {followers}\nTakip Edilen Sayısı: {following}\nGönderi Sayısı: {posts}"
            window["-INFO-"].update(info_text)
            profile_pic_path = save_profile_pic(profile_pic_url)
            profile_pic_data = Image.open(profile_pic_path)
            profile_pic_data.thumbnail((150, 150))  # Profil resmini boyutlandır
            profile_pic_bytes = ImageTk.PhotoImage(profile_pic_data)
            window["-PROFILE_PIC-"].update(data=profile_pic_bytes)
    elif event == "Takipçi ve Takip Edilenleri Al":
        username = values["-USERNAME-"]
        password = values["-PASSWORD-"]
        get_followers_and_followees(username, password)
    elif event == "Takip Etmeyenleri Bul":
        find_unfollowers()
    elif event == "Tümünü Çık":
        result = sg.popup_ok_cancel("Takip etmeyen tüm kullanıcılardan çıkmak istediğinize emin misiniz?", title="Takip Etme İşlemi", keep_on_top=True)
        if result == "OK":
            # Takipten çıkış işlemi
            try:
                L = instaloader.Instaloader()
                L.login(username, password)
                with open("following.txt", "r") as f:
                    for line in f:
                        user = line.strip()
                        if user in unfollowers:
                            L.unfollow(user)
                sg.popup("Takipten çıkıldı!")
            except Exception as e:
                sg.popup_error("Takipten çıkış sırasında bir hata oluştu: " + str(e))
    elif event == "Takipçi İstiyor Musunuz?":
        result = sg.popup_yes_no("Takipçi istiyor musunuz?", title="Takipçi İsteme İşlemi", keep_on_top=True)
        if result == "Yes":
            try:
                L = instaloader.Instaloader()
                L.login(username, password)
                with open("followers.txt", "r") as f:
                    followers_list = f.read().splitlines()
                random.shuffle(followers_list)
                if followers_list:
                    for follower in followers_list[:10]:
                        L.follow(follower)
                    sg.popup("Takipçi gönderildi!")
                else:
                    sg.popup("Takipçi bulunamadı!")
            except Exception as e:
                sg.popup_error("Takipçi gönderimi sırasında bir hata oluştu: " + str(e))

# Pencereyi kapat
window.close()
