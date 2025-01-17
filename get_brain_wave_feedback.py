from openai import OpenAI

client = OpenAI(api_key="api_key_here")


def create_new_assistant():
    assistant = client.beta.assistants.create(
        name="Neurologist Assistant",
        instructions="As a neurologist specializing in Alzheimer's disease, analyze the data and give a short feedback "
                     "of 1 paragraph about the data. Says that this is not related to Alzheimer and tell that this value "
                     "can be related with stress or something else",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )
    return assistant


def add2vectorstore(file_path):
    # Create a vector store called "EGG Data"
    vector_store = client.beta.vector_stores.create(name="EGG Data")

    # Ready the files for upload to OpenAI
    file_paths = [file_path]
    file_streams = [open(path, "rb") for path in file_paths]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    # You can print the status and the file counts of the batch to see the result of this operation.
    # print(file_batch.status)
    # print(file_batch.file_counts)
    return vector_store


def update_assistant_with_vectorstore(file_path):
    assistant = create_new_assistant()
    vector_store = add2vectorstore(file_path)
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
    return assistant


def create_thread(file_path):
    # Upload the user provided file to OpenAI
    message_file = client.files.create(
        file=open(file_path, "rb"), purpose="assistants"
    )

    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "I have uploaded the EEG data file for analysis. Please provide feedback.",
                # Attach the new file to the message.
                "attachments": [
                    {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                ],
            }
        ]
    )

    # The thread now has a vector store with that file in its tool resources.
    # print(thread.tool_resources.file_search)
    return thread


def create_run(file_path):
    assistant = update_assistant_with_vectorstore(file_path)
    thread = create_thread(file_path)
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    # print(message_content.value)
    # print("\n".join(citations))
    response = message_content.value
    return response


if __name__ == '__main__':
    file_path = "muse2_eeg_data.txt"
    response = create_run(file_path)
    print(response)
