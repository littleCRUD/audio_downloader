from pytube import YouTube


# Функция загрузки аудио
async def dowmload_audio(url: str):
    destination = "downloads"
    audio = YouTube(url=url).streams.filter(only_audio=True, file_extension='mp4').first()
    title = YouTube(url=url).title
    file_out = audio.download(output_path=destination, filename='temp.mp4')
    return file_out, title




