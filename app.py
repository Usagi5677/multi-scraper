import gradio as gr
from bs4 import BeautifulSoup
import os
from datetime import datetime
import math
import threading
import psutil
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
import time
from theme_dropdown import create_theme_dropdown
from websites import get_urls
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from ui_components import FormRow, ToolButton
import hashlib

DIRECTORY = f"output"
THREAD_COUNT = 2 * psutil.cpu_count() // psutil.cpu_count(logical=False)
THREAD_LIST = []
LIST_OF_IMAGES = []
FLAG = False
PROCESSED_URLS = []
DARK_MODE_SYMBOL = '\U0001F319'  # 🌙
DUPLICATE_LIST = []
FILE_HASHES = {}

dropdown, js = create_theme_dropdown()

# downloads the image from url


def download(start, end, urls, pause):
    global DIRECTORY
    global PROCESSED_URLS
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    directory = os.path.join(f'output', timestamp)
    DIRECTORY = directory
    os.makedirs(directory, exist_ok=True)
    for i in range(start, end):
        try:
            url = urls[i]
            extension = os.path.splitext(url)[1]  # get the file extension
            filename = os.path.basename(url)  # get the filename from the URL
            if (len(filename) > 100):
                filename = str(i+1)
            if (len(extension) > 6):
                extension = ".png"
            # Remove the extension and anything after it
            filename = re.sub(rf"{re.escape(extension)}.*$", "", filename)
            filename = f"{filename}{extension}"
            filepath = os.path.join(directory, filename)

            if (pause > 0):
                time.sleep(pause)
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            with open(filepath, 'wb') as f:
                f.write(webpage)

            # add path to array to show later in gallery
            LIST_OF_IMAGES.append(filepath)
            PROCESSED_URLS.append(url)
        except HTTPError as e:
            global FLAG
            FLAG = True
            print(f"HTTP Error {e.code}: {url}")
            return
        except URLError as e:
            print(f"URL Error: {e.reason}")
        except Exception as e:
            print(f"Error: {str(e)}")


def scraper(link, user_agent, injected, show_maximum_number_of_image_slider, maximum_number_of_image, type_checkboxes, pause, show_bulk_file, bulk_file, headless):
    global LIST_OF_IMAGES
    global THREAD_LIST
    global FLAG
    global DIRECTORY
    global PROCESSED_URLS
    LIST_OF_IMAGES = []  # reset list of image path
    THREAD_LIST = []  # reset threads
    PROCESSED_URLS = []
    FLAG = False

    if not re.match(r'https?://', link):
        link = "https://" + link

    if not re.match(r'https?://([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?', link):
        return

    pause = abs(pause)  # -1 will be 1
    links = []
    if (show_bulk_file and bulk_file is not None):
        links = read_urls(bulk_file)
        link = ""

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    user_home = os.path.expanduser("~")
    chrome_data_dir = os.path.join(
        user_home, "AppData", "Local", "Google", "Chrome", "User Data")
    options.add_argument(f"user-data-dir={chrome_data_dir}")
    options.add_argument("--no-sandbox")
    if (headless):
        options.add_argument("--headless")

    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    options.add_argument(f'user-agent={user_agent}')

    cwd = os.getcwd()
    os.makedirs(f"driver", exist_ok=True)
    
    driver_path = os.path.join(cwd, 'driver', 'chromedriver.exe')
    service = Service(executable_path='C:\Program Files\Chrome Driver\chromedriver.exe',)
    driver = webdriver.Chrome(service=service, options=options)
    #driver = webdriver.Chrome(executable_path=driver_path, options=options)

    urls = []
    if (len(links) > 0):
        for link in links:
            new_urls = get_urls(driver, link, injected=injected,
                                pause=pause, headless=headless)
            urls.extend(new_urls)

    else:
        urls = get_urls(driver, link, injected=injected,
                        pause=pause, headless=headless)

    if maximum_number_of_image is not None and (maximum_number_of_image <= len(urls)) and show_maximum_number_of_image_slider:
        urls = urls[:maximum_number_of_image]

    allowed_types = type_checkboxes

    urls = [url for url in urls if any(url.endswith(
        "." + allowed_type) for allowed_type in allowed_types)]

    local_thread_list = []

    for i in range(THREAD_COUNT):
        start = math.floor(i * len(urls) / THREAD_COUNT)
        end = math.floor((i + 1) * len(urls) / THREAD_COUNT)

        t = threading.Thread(target=download, daemon=True, args=(
            start, end, urls, pause))
        local_thread_list.append(t)
        THREAD_LIST.append(t)

    for thread in local_thread_list:
        thread.start()

    for thread in THREAD_LIST:
        thread.join()

    driver.close()
    driver.quit()
    return LIST_OF_IMAGES

# reading text file for bulk url


def read_urls(file):
    with open(file.name) as f:
        contents = f.read().replace("\n", "")
    urls = contents.strip().split(",")
    return urls


def find_duplicate_files(misc_directory):

    global DUPLICATE_LIST
    global THREAD_LIST
    global FILE_HASHES
    DUPLICATE_LIST = []  # reset list
    THREAD_LIST = []  # reset threads
    FILE_HASHES = {}  # reset hash list

    local_thread_list = []
    file_count = 0

    for root, dirs, files in os.walk(misc_directory):
        file_count += len(files)

    for root, dirs, files in os.walk(misc_directory):
        for filename in files:
            # Get the full path of the file
            filepath = os.path.join(root, filename)
            with open(filepath, 'rb') as file:
                file_hash = hashlib.md5(file.read()).hexdigest()
            if file_hash in FILE_HASHES:
                DUPLICATE_LIST.append(filepath)
            else:
                # Add the hash and file path to the dictionary
                FILE_HASHES[file_hash] = filepath

    duplicate_files = count_duplicate_files()
    output = f"Total files: {file_count}\n\n"
    if(len(DUPLICATE_LIST) <= 0 ):
        output += f"No duplicate file found."
    for extension, count in duplicate_files.items():
        output += f"Duplicate files with extension [ {extension} ]: {count}\n"
    return output


def remove(start, end, duplicate_list):
    try:
        for i in range(start, end):
            for file in duplicate_list:
                os.remove(file)
    except Exception as e:
        print(f"Error: {str(e)}")


def remove_duplicates(misc_directory):
    if (len(DUPLICATE_LIST) > 0):
        local_thread_list = []
        file_count = len(DUPLICATE_LIST)
        total_files = 0
        for root, dirs, files in os.walk(misc_directory):
            total_files += len(files)
        duplicate_files = count_duplicate_files()
        for i in range(THREAD_COUNT):
            start = math.floor(i * file_count / THREAD_COUNT)
            end = math.floor((i + 1) * file_count / THREAD_COUNT)

            t = threading.Thread(target=remove, daemon=True, args=(
                start, end, DUPLICATE_LIST, ))
            local_thread_list.append(t)
            THREAD_LIST.append(t)

        for thread in local_thread_list:
            thread.start()

        for thread in THREAD_LIST:
            thread.join()
        output = f"Total files: {total_files}\n\n"
        for extension, count in duplicate_files.items():
            output += f"Duplicate files with extension [ {extension} ]: {count}\n"

        output += f"\nSuccessfully removed {sum(duplicate_files.values())} files."
        return output

def count_duplicate_files():
    file_count = {}
    for file in DUPLICATE_LIST:
            _, extension = os.path.splitext(file)
            if extension not in file_count:
                file_count[extension] = 1
            else:
                file_count[extension] += 1

    return file_count


css = ""
cssfile = f"style.css"
with open(cssfile, "r", encoding="utf8") as file:
    css += file.read() + "\n"


def gr_show(visible=True):
    return {"visible": visible, "__type__": "update"}


with gr.Blocks(analytics_enabled=False,) as scraper_interface:
    with FormRow():
        with gr.Box(elem_id="link_textbox"):
            text = gr.Textbox(
                label="Link",
                show_label=False,
                max_lines=1,
                placeholder="Enter your link",
            ).style(
                container=False,
            )
        with gr.Box(elem_id="link_textbox"):
            user_agent = gr.Textbox(
                label="User Agent",
                show_label=False,
                max_lines=1,
                placeholder="Enter your user-agent",
            ).style(
                container=False,
            )

        submit = gr.Button("Download", elem_id="scraper_submit",
                           variant='primary',).style(full_width=False, )
        cancel = gr.Button('Cancel', elem_id="scraper_cancel", ).style(
            full_width=False, )
        toggle_dark = ToolButton(value=DARK_MODE_SYMBOL, elem_id="darkmode", ).style(
            full_width=False, size="sm")

    components = []
    components2 = []
    with FormRow():
        with gr.Column():
            with FormRow(elem_id="scraper_checkboxes", variant="compact"):
                injected = gr.Checkbox(
                    label='Injected', value=False, elem_id="scraper_injected")
                show_maximum_number_of_image_slider = gr.Checkbox(
                    label='Maximum number of image', value=False, elem_id="show_maximum_number_of_image_slider", variant="compact")
                show_bulk_file = gr.Checkbox(
                    label='Bulk', value=False, elem_id="show_bulk_file")
                headless = gr.Checkbox(
                    label='Headless', value=True, elem_id="scraper_headless")
            with FormRow(elem_id="scraper_maximum_number_of_image_row", visible=False) as maximum_number_of_image_row:
                components.append(maximum_number_of_image_row)
                maximum_number_of_image = gr.Slider(
                    minimum=1, maximum=500, label="Maximum number of image", value=1, elem_id="scraper_maximum_number_of_image")
            with FormRow(elem_id="scraper_file", visible=False) as bulk_file_row:
                bulk_file = gr.File(file_types=[".txt"])
                components2.append(bulk_file_row)
            with FormRow(elem_id="scraper_type_checkboxes", ):
                type_checkboxes = gr.CheckboxGroup(label="Types", value=["jpg", "png", "gif", "webm"], choices=[
                                                   "jpg", "png", "gif", "webm"], elem_id="type_checkboxes")
            with FormRow(elem_id="scraper_pause",):
                pause = gr.Number(label="Pause", value=0,)
        with gr.Column(scale=10):
            gallery = gr.Gallery(
                label="Downloaded Images", show_label=True, elem_id="gallery",).style(columns=[3], rows=[3], object_fit="contain", height="auto")

    def change_visibility(show):
        return {comp: gr_show(show) for comp in components}

    def change_visibility2(show):
        return {comp: gr_show(show) for comp in components2}
    show_maximum_number_of_image_slider.change(change_visibility, show_progress=False, inputs=[
                                               show_maximum_number_of_image_slider], outputs=maximum_number_of_image_row)
    show_bulk_file.change(change_visibility2, show_progress=False, inputs=[
        show_bulk_file], outputs=bulk_file_row)
    submit_event = submit.click(fn=scraper, inputs=[
                                text, user_agent, injected, show_maximum_number_of_image_slider, maximum_number_of_image, type_checkboxes, pause, show_bulk_file, bulk_file, headless], outputs=gallery)

    cancel.click(fn=None, inputs=None, outputs=None, cancels=[submit_event])

with gr.Blocks(analytics_enabled=False,) as misc_interface:
    with FormRow():
        misc_directory = gr.Textbox(label="directory",
                                    show_label=False,
                                    max_lines=1,
                                    placeholder="Directory",).style(
            container=False,
        )
        misc_submit = gr.Button("Submit", elem_id="misc_submit",
                                variant='primary',).style(full_width=False, )
        misc_cancel = gr.Button('Cancel', elem_id="misc_cancel", ).style(
            full_width=False, )
        misc_toggle_dark = ToolButton(value=DARK_MODE_SYMBOL, elem_id="darkmode", ).style(
            full_width=False, size="sm")

    result_text = gr.TextArea(
        label="output",
        show_label=False,
        max_lines=1,
        placeholder="output",
    ).style(
        container=False,
    )
    misc_remove = gr.Button("Remove", elem_id="misc_submit", visible=True,
                            variant='primary',).style(full_width=True, )
    
    misc_remove_event = misc_remove.click(
        fn=remove_duplicates, inputs=[misc_directory], outputs=result_text)
    misc_submit_event = misc_submit.click(
        fn=find_duplicate_files, inputs=[misc_directory], outputs=result_text)
    
    misc_cancel.click(fn=None, inputs=None, outputs=None,
                      cancels=[misc_submit_event, misc_remove_event])


interfaces = [
    (scraper_interface, "scraper", "scraper"),
    (misc_interface, "remove duplicate", "misc"),
]

with gr.Blocks(analytics_enabled=False, css=css, title="Multi-Scraper", ) as demo:
    with gr.Column():
        with gr.Row().style(equal_height=True):
            with gr.Column():
                gr.Markdown(
                    """
                    # Data Scraper: `Image`
                    To use this, enter the link & an user-agent.
                    you can find your user-agent from the internet, e.g. https://www.whatismybrowser.com/detect/what-is-my-user-agent/
                    note: some websites may not work
                    """
                )

        with gr.Tabs(elem_id="tabs") as tabs:
            for interface, label, ifid in interfaces:
                with gr.TabItem(label, id=ifid, elem_id='tab_' + ifid):
                    interface.render()
    toggle_dark.click(
        None,
        _js="""
        () => {
            document.body.classList.toggle('dark');
            document.querySelector('gradio-app').style.backgroundColor = 'var(--color-background-primary)'
        }
        """,
    )
    misc_toggle_dark.click(
        None,
        _js="""
        () => {
            document.body.classList.toggle('dark');
            document.querySelector('gradio-app').style.backgroundColor = 'var(--color-background-primary)'
        }
        """,
    )


if __name__ == "__main__":
    demo.queue(concurrency_count=2, max_size=20).launch(show_error=True)
