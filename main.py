import cv2 as cv
import numpy as np
import time


def zmanjsaj_sliko(slika, sirina, visina):
    '''Zmanjšaj sliko na velikost sirina x visina.'''
    return cv.resize(slika, (sirina, visina))


def obdelaj_sliko_s_skatlami(slika, sirina_skatle, visina_skatle, barva_koze) -> list:
    '''Sprehodi se skozi sliko v velikosti škatle (sirina_skatle x visina_skatle) in izračunaj število pikslov kože v vsaki škatli.
    Škatle se ne smejo prekrivati!
    Vrne seznam škatel, s številom pikslov kože.
    Primer: Če je v sliki 25 škatel, kjer je v vsaki vrstici 5 škatel, naj bo seznam oblike
      [[1,0,0,1,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,1]].
      V tem primeru je v prvi škatli 1 piksel kože, v drugi 0, v tretji 0, v četrti 1 in v peti 1.'''

    visina, sirina, _ = slika.shape
    rezultat = []

    for y in range(0, visina, visina_skatle):  # 0 -> zacen od (0,0) visina -> konca vrednost visina_skatle -> korak
        vrstica = []
        for x in range(0, sirina, sirina_skatle):
            x1, y1 = x, y
            x2, y2 = x + sirina_skatle, y + visina_skatle

            # Process the box (dummy count for now)
            st_pikslov_koze = prestej_piklse_z_barvo_koze(slika[y1:y2, x1:x2],barva_koze)
            vrstica.append(st_pikslov_koze)

        rezultat.append(vrstica)

    return rezultat


def prestej_piklse_z_barvo_koze(slika, barva_koze) -> int:
    '''Prestej število pikslov z barvo kože v škatli.'''
    visina, sirina, _ =  slika.shape
    rezultat = 0
    for y in range(0, visina, 1):
        for x in range(0, sirina, 1):
            barva_piksla = tuple(slika[y, x])  # Convert pixel to (R, G, B) tuple

            # Check if the pixel is within ±10% of the reference skin color
            if all(abs(int(barva_piksla[i]) - int(barva_koze[i])) <= int(barva_koze[i]) * 0.1 for i in range(3)):
                rezultat += 1

        #print(rezultat)
    return rezultat



def doloci_barvo_koze(slika, levo_zgoraj, desno_spodaj) -> tuple:
    '''Ta funkcija se kliče zgolj 1x na prvi sliki iz kamere.
    Vrne barvo kože v območju ki ga definira oklepajoča škatla (levo_zgoraj, desno_spodaj).
      Način izračuna je prepuščen vaši domišljiji.'''

    x1, y1 = levo_zgoraj
    x2, y2 = desno_spodaj

    x = slika[y1:y2, x1:x2]

    avg_color = tuple(map(int, np.mean(x, axis=(0, 1))))
    return avg_color


if __name__ == '__main__':
    # Pripravi kamero

    kamera = cv.VideoCapture(0)

    kamera.set(cv.CAP_PROP_FRAME_WIDTH, 280)  # Set width to 280
    kamera.set(cv.CAP_PROP_FRAME_HEIGHT, 320)  # Set height to 320

    start_time = time.time()
    if not kamera.isOpened():
        print('Kamera ni bila odprta.')
    else:
        while True:
            # Preberemo sliko iz kamere
            ret, slika = kamera.read()


            cv.imshow('Kamera',cv.flip(slika,1))

            # Počaka 3 sekunda potem pa shrani sliko
            if time.time() - start_time >= 3:
                cv.imwrite('screenshot.png', slika)
                print("Screenshot saved as 'screenshot.png'")
                break

            # Če pritisnemo tipko 'q', zapremo okno
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        # Zapremo okno
        kamera.release()
        cv.destroyAllWindows()

    # Zajami prvo sliko iz kamere
    slika = cv.imread('screenshot.png')
    obdelana_slika = zmanjsaj_sliko(slika, 280, 320)

    top_left = (100, 100)
    bottom_right = (180, 220)
    color = (255, 0, 0)
    thickness = 2
    cv.rectangle(obdelana_slika, top_left, bottom_right, color, thickness)

    barva = doloci_barvo_koze(obdelana_slika, top_left, bottom_right)

    print("Povprečna barva kože:", barva)
    sirina_skatle, visina_skatle = 20, 10
    visina, sirina, _ = obdelana_slika.shape
    obdelaj_sliko_s_skatlami(obdelana_slika,sirina_skatle,visina_skatle,barva)

    skatle = obdelaj_sliko_s_skatlami(obdelana_slika,sirina_skatle,visina_skatle,barva)

    for i, vrstica in enumerate(skatle):  # Loop through rows
        for j, st_pikslov in enumerate(vrstica):  # Loop through elements in a row
            x1, y1 = j * sirina_skatle, i * visina_skatle
            x2, y2 = x1 + sirina_skatle, y1 + visina_skatle

            if st_pikslov >= 2:
                cv.rectangle(obdelana_slika, (x1, y1), (x2, y2), (0, 255, 0), 1)  # Draw a green rectangle

    cv.imshow('Slika',obdelana_slika)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # Izračunamo barvo kože na prvi sliki

    # Zajemaj slike iz kamere in jih obdeluj

    # Označi območja (škatle), kjer se nahaja obraz (kako je prepuščeno vaši domišljiji)
    # Vprašanje 1: Kako iz števila pikslov iz vsake škatle določiti celotno območje obraza (Floodfill)?
    # Vprašanje 2: Kako prešteti število ljudi?

    # Kako velikost prebirne škatle vpliva na hitrost algoritma in točnost detekcije? Poigrajte se s parametroma velikost_skatle
    # in ne pozabite, da ni nujno da je škatla kvadratna.
    pass