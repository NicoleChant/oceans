import pytz

madrid_timezone = pytz.timezone("Europe/Madrid")

WEBCAM_LOCATIONS = {
    "Nigran": "https://waira.com/webcam/",  #<---- predicting!!!
    "ElPorto": "https://hdontap.com/index.php/video/stream/el-porto-surf-cam", #FINISHED
    "Zarautz": "https://quiksilver.es/surf/webcams/zarautz.html?src=shipping_b",
    "Hawai": "https://explore.org/livecams/hawaii/hawaii-pipeline-cam",
    "La Coruna": "https://www.camaramar.com/webcam-playas/galicia/acoru%C3%B1a/doninos"
}

URLs = [
    "https://waira.com/webcam/",  #YES
    "https://hdontap.com/index.php/video/stream/el-porto-surf-cam",  #YES
    "https://www.youtube.com/watch?v=kU6btDXVdxw",  #NO
    "https://www.youtube.com/watch?v=n_e-kzztGIU",  #NO
    "https://www.tablassurfshop.com/webcam-salinas",  #NO
    "https://quiksilver.es/surf/webcams/zarautz.html?src=shipping_b",  #YES
    "https://quiksilver.es/surf/webcams/guethary.html?src=shipping_b",  #NO
    "https://www.camaramar.com/webcam-playas/galicia/acoru%C3%B1a/doninos",  #YES
    "https://www.surfoutlook.com/surfcam/mexico/k-38",  #NO
    "https://explore.org/livecams/hawaii/hawaii-pipeline-cam"  #YES
]
