from celery import shared_task

@shared_task
def veri_cekme_gorevi():
    print("🔹 Veri çekme görevi çalıştı!")
    # Buraya veri çekme kodlarını ekleyebilirsin.
    return "Veri başarıyla çekildi!"
