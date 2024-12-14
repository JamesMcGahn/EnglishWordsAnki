from time import sleep

import google
from google.cloud import texttospeech
from PySide6.QtCore import QObject, Signal, Slot

from utils.files.path_manager import PathManager


class GoogleAudioWorker(QObject):
    success = Signal(str)
    error = Signal(str)
    finised = Signal()
    start_work = Signal()

    def __init__(
        self,
        text,
        filename,
        folder_path="./",
        access_key_location="./key.json",
    ):
        super().__init__()
        self.text = text
        self.google_tried = False
        self.filename = filename
        self.folder_path = folder_path
        self.access_key_location = access_key_location
        self.start_work.connect(self.do_work)

    @Slot()
    def do_work(self):
        print("Starting Google Audio Worker...")
        print(f"google woker in thread {self.thread()}")
        try:
            client = texttospeech.TextToSpeechClient.from_service_account_json(
                self.access_key_location
            )

            input_text = texttospeech.SynthesisInput(text=self.text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                request={
                    "input": input_text,
                    "voice": voice,
                    "audio_config": audio_config,
                }
            )

            path = PathManager.check_dup(self.folder_path, self.filename, ".mp3")

            with open(path, "wb") as out:
                out.write(response.audio_content)
            print("wrote file")
            self.success.emit(path)

        except google.api_core.exceptions.ServiceUnavailable as e:
            if self.google_tried is False:
                failure_msg_retry = "Failed to get Audio From Google...Trying Again..."
                print(failure_msg_retry)
                self.error.emit(failure_msg_retry)
                sleep(15)
                self.google_tried = True
                self.do_work(text=self.text, filename=self.filename)
            else:
                print("Failed to get Audio From Google")
                return False
        except Exception as e:
            print("An error occurred:", e)
            self.error.emit(str(e))
            return False

        finally:
            self.finised.emit()
