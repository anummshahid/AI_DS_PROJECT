import os
import platform
import shutil
import eel
from engine.features import *

eel.init('www')

playAssistantSound()

def open_in_chrome_app(url: str) -> None:
	"""Open the given URL in Chrome app mode when possible, with sensible fallbacks.

	Works on macOS, Windows and common Linux setups. Falls back to the system default
	browser when Chrome is not available.
	"""
	system = platform.system()
	# macOS
	if system == 'Darwin':
		# Prefer opening with Google Chrome in app mode
		chrome_app_path = '/Applications/Google Chrome.app'
		if os.path.exists(chrome_app_path):
			os.system(f'open -a "Google Chrome" --args --app="{url}"')
			return
		# fallback to default browser
		os.system(f'open "{url}"')
		return

	# Windows
	if system == 'Windows':
		# start is the usual way on Windows; keep original behaviour if chrome exists
		if shutil.which('chrome') or shutil.which('chrome.exe'):
			os.system(f'start chrome.exe --app="{url}"')
			return
		os.system(f'start "" "{url}"')
		return

	# Linux / other
	# Try common chrome binaries first, then fall back to xdg-open
	for chrome_cmd in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
		if shutil.which(chrome_cmd):
			os.system(f'{chrome_cmd} --app="{url}" &')
			return
	# last resort: open with default handler
	if shutil.which('xdg-open'):
		os.system(f'xdg-open "{url}"')
	else:
		# If nothing else, leave to eel to open default browser (mode=None)
		return


url = 'http://localhost:8000/index.html'
open_in_chrome_app(url)
eel.start('index.html', size=(1000, 600), port=8000)