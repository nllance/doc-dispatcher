import zipfile, os, shutil, platform
from pathlib import Path
import re
import textract
import langdetect

# Extract content from rich text and detect the languae
def detect_language(source):
    text = textract.process(source).decode('utf-8').lower()
    lang = langdetect.detect(text)
    return lang, text

# Take a zip file, and extract them to a temporary directory
def extract_files(file_path, des_dir):
    # Create a temporary directory
    temp_path = Path(des_dir + '/temp')
    if os.path.isdir(temp_path):
        shutil.rmtree(temp_path)        
    os.mkdir(temp_path)

    # Extract the zip file
    path_to_zip_file = Path(file_path)
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_path)

    extracted_dirs = os.listdir(temp_path)
    messages = []

    # Go through each extracted directory
    for extracted_dir in extracted_dirs:
        # Get client ID and name, and validate ID
        student = extracted_dir.split(' ')
        id = ''.join(filter(str.isdigit, student[0]))
        if (int(id) > 999) or (int(id) < 100):
            return [extracted_dir + ' does not have valid Client ID.']
        name = student[1]

        zip_file_name = os.path.basename(path_to_zip_file)
        # Determine destination path based on location
        if student[0][:2]=='HK':
            messages.extend(save_to_folder('HK', id, name, des_dir, zip_file_name, extracted_dir))
        else:
            messages.extend(save_to_folder('CA', id, name, des_dir, zip_file_name, extracted_dir))

    messages.append('Finished processing ' + zip_file_name)
    return messages


# Save the file to appropriate directory
def save_to_folder(location, id, name, des_dir, zip_file_name, source_folder):
    save_path = ''
    if platform.system == 'Windows':
        if location == 'HK':
            save_path = des_dir + '\iDC HK - Documents\Customer\Customer Profile'
        if location == 'CA':
            save_path = des_dir + '\iDC Canada - Documents\Customer\Customer Profile'

    else:
        if location == 'HK':
            save_path = des_dir + '/iDC HK - Documents/Customer/Customer Profile'
        if location == 'CA':
            save_path = des_dir + '/iDC Canada - Documents/Customer/Customer Profile'

    # The destination path
    data_folder = Path(save_path)
    if not os.path.exists(data_folder):
        return [save_path + ' does not exist.']

    folders = os.listdir(data_folder)
    sub_folder = ''
    temp_path = Path(des_dir + '/temp')
    pre_text = ''

    # Determine the name of the subfolder
    # Leave pre_text for further processing if resume/cover letter/interview QA
    lower_zip_file = zip_file_name.lower()
    if 'idc academy homework' in lower_zip_file:
        sub_folder = '3. Online Learning, MAPP & Job Searching Homework'
        pre_text = 'iDC Academy Homework - '

    if 'job postings research assignment' in lower_zip_file:
        sub_folder = '3. Online Learning, MAPP & Job Searching Homework'
        pre_text = 'Job Postings Research Assignment - '

    if ('resume' or 'cover letter') in lower_zip_file:
        sub_folder = '4. Resume & Cover Letter'

    if 'interview qa' in lower_zip_file:
        sub_folder = '5. Interview'

    if 'interview debriefing' in lower_zip_file:
        sub_folder = '5. Interview'
        pre_text = 'Interview Debriefing Question List - '

    if 'feedback to mentor' in lower_zip_file:
        sub_folder = '6. Coaching Feedback'
        pre_text = 'iDC Feedback Form on Mentor - '

    if 'offer' in lower_zip_file:
        sub_folder = '7. Offer & Background Info'

    if sub_folder == '':
        return [zip_file_name + ' cannot be mapped by name of assignment.']

    # Each item is the directory for an individual client
    for item in folders:
        folder_id = ''.join(filter(str.isdigit, item))

        # Check if the client ID matches with source
        if folder_id == id:
            destination_folder = data_folder/item/sub_folder
            if not os.path.exists(destination_folder):
                return [source_folder + ' cannot be mapped by name of assignment.']

            source_directory = temp_path/source_folder
            messages = []

            # All files from the extracted source directory
            for file_name in os.listdir(source_directory):
                source = source_directory/file_name 
                
                # No renaming for offers
                if sub_folder == '7. Offer & Background Info':
                    new_file_name = file_name
                
                # Otherwise rename the files
                else:
                    # Determine pre_text for resume/cover letter/interview QA
                    lower_file_name = file_name.lower()
                    if sub_folder == '4. Resume & Cover Letter':
                        if 'resume' in lower_file_name:
                            pre_text = 'Resume - '
                        elif 'cover letter' in lower_file_name:
                            pre_text = 'Cover Letter - '
                        elif '简历' in file_name:
                            pre_text = '简历 - '
                        elif detect_language(source)[0] == 'en':
                            if 'resume' in detect_language(source)[1]:
                                pre_text = 'Resume - '
                            elif 'cover letter' in detect_language(source)[1]:
                                pre_text = 'Cover Letter - '
                        elif detect_language(source)[0] == 'zh-cn':
                            pre_text = '简历 - '

                    if sub_folder == '5. Interview':
                        if pre_text != 'Interview Debriefing Question List - ':
                            if 'technical' in lower_file_name:
                                pre_text = 'Technical Interview Q&A – '
                            elif detect_language(source)[0] == 'en':
                                if 'technical' in detect_language(source)[1]:
                                    pre_text = 'Technical Interview Q&A – '
                            elif detect_language(source)[0] == 'zh-cn':
                                pre_text = '中文面试 Q&A - '
                            else:
                                pre_text = 'Interview Q&A – '

                    # Get file extension
                    extension = file_name.split('.')[-1]

                    # Get file version
                    version = 0; updated = ''
                    files_in_des = os.listdir(destination_folder)
                    for file in files_in_des:
                        # "Technical Interview" and "Interview" should not match
                        if pre_text == 'Interview Q&A – ' and ('Technical Interview Q&A – ' in file):
                            continue
                        # Otherwise, try match pre_text with existing file names
                        elif pre_text.lower() in file.lower():
                            match = re.search(r"v[0-9]", file.lower())
                            if match != None:
                                # Index of the match in the file name
                                index = match.start() + 1
                                # The version of this file
                                this_v = 0
                                while (True):
                                    try:
                                        this_v = this_v * 10 + int(file[index])
                                        index += 1
                                    except:
                                        break
                                # Decide if the version of this file is bigger than currently recorded
                                if this_v > version:
                                    version = this_v
                                    # Detect keywords if we update the version number
                                    if 'final' in file.lower():
                                        if 'updated' in file.lower():
                                            updated = ' - second updated'
                                        else:
                                            updated = ' - updated'
                                    else:
                                        updated = ''
                    version += 1
                
                    new_file_name = pre_text + id + ' - ' + name + ' - V' + str(version) + updated + '.' + extension

                # Dispatch the file
                destination = destination_folder/new_file_name
                if os.path.isfile(source):
                    shutil.move(source, destination)
                    messages.append('New file created at ' + str(destination))

            return messages
        
    return [source_folder + ' cannot be mapped by Client ID.']
    