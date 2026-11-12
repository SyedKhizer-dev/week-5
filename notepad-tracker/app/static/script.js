
const directoryInput = document.getElementById("directory-path");
const loadDirectoryBtn = document.getElementById("load-directory-btn");
const refreshFilesBtn = document.getElementById("refresh-files-btn");
const fileList = document.getElementById("file-list");

const editor = document.getElementById("editor");
const currentFilename = document.getElementById("current-filename");
const saveStatus = document.getElementById("save-status");
const filePathDisplay = document.getElementById("file-path");
const characterCount = document.getElementById("character-count");

const newFileBtn = document.getElementById("new-file-btn");
const saveFileBtn = document.getElementById("save-file-btn");
const initGitBtn = document.getElementById("init-git-btn");
const historyBtn = document.getElementById("history-btn");

const historyPanel = document.getElementById("history-panel");
const historyList = document.getElementById("history-list");
const closeHistoryBtn = document.getElementById("close-history-btn");

const AUTOSAVE_DELAY = Number(editor.dataset.autosaveDelay) || 2000;

let currentDirectory = null;
let currentFilePath = null;

let saveTimer = null;
let saveInProgress = false;
let saveAgain = false;
let savePromise = null;

let editVersion = 0;
let savedVersion = 0;

let directoryRequestId = 0;
let fileRequestId = 0;


async function apiRequest(url, options = {}) {

    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(
            result.error || result.details || `Request failed: ${response.status}`
        );
    }

    return result;
}


function setStatus(message, type = "") {

    saveStatus.textContent = message;

    saveStatus.className = "status";

    if (type) {
        saveStatus.classList.add(type);
    }
}


function updateCharacterCount() {

    characterCount.textContent = `${editor.value.length} characters`;
}


function updateFileList(files) {

    fileList.replaceChildren();

    if (files.length === 0) {

        const message = document.createElement("p");

        message.className = "empty-message";
        message.textContent = "This directory is empty.";

        fileList.appendChild(message);

        return;
    }

    files.forEach(file => {

        const item = document.createElement("div");

        item.className = "file-item";
        item.dataset.path = file.path;

        if (file.path === currentFilePath) {
            item.classList.add("active");
        }

        item.textContent = `${file.is_directory ? "Folder" : "File"}: ${file.name}`;

        item.addEventListener("click", async () => {

            if (file.is_directory) {

                directoryInput.value = file.path;

                await loadDirectory(file.path);

            } else {

                await openFile(file.path);
            }
        });

        fileList.appendChild(item);
    });
}


function updateFileListForCurrentFile() {

    const items = fileList.querySelectorAll(".file-item");

    items.forEach(item => {

        item.classList.toggle(
            "active",
            item.dataset.path === currentFilePath
        );

    });
}


async function loadDirectory(path = directoryInput.value.trim()) {

    if (!path) {
        setStatus("Enter a directory path", "error");
        return;
    }

    if (currentFilePath && editVersion > savedVersion) {

        const saved = await saveFile();

        if (!saved) {
            setStatus("Save failed. Directory not changed.", "error");
            return;
        }
    }

    const requestId = ++directoryRequestId;

    setStatus("Loading directory...");

    try {

        const query = new URLSearchParams({ path });

        const result = await apiRequest(`/api/files?${query}`);

        if (requestId !== directoryRequestId) {
            return;
        }

        currentDirectory = result.directory;

        directoryInput.value = result.directory;

        initGitBtn.disabled = false;

        updateFileList(result.files);

        setStatus("Directory loaded", "saved");

    } catch (error) {

        if (requestId === directoryRequestId) {
            setStatus(error.message, "error");
        }
    }
}


async function openFile(path) {

    if (currentFilePath && editVersion > savedVersion) {

        const saved = await saveFile();

        if (!saved) {
            setStatus("Save failed. File not changed.", "error");
            return;
        }
    }

    const requestId = ++fileRequestId;

    setStatus("Opening file...");

    try {

        const result = await apiRequest("/api/files/open", {
            method: "POST",
            body: JSON.stringify({ path })
        });

        if (requestId !== fileRequestId) {
            return;
        }

        currentFilePath = result.path;

        editor.value = result.content;

        editor.disabled = false;

        saveFileBtn.disabled = false;
        historyBtn.disabled = false;

        currentFilename.textContent = currentFilePath.split(/[\\/]/).pop();

        filePathDisplay.textContent = currentFilePath;

        editVersion = 0;
        savedVersion = 0;

        updateCharacterCount();

        updateFileListForCurrentFile();

        setStatus("File opened", "saved");

    } catch (error) {

        if (requestId === fileRequestId) {
            setStatus(error.message, "error");
        }
    }
}


function scheduleAutosave() {

    if (!currentFilePath) {
        return;
    }

    editVersion++;

    setStatus("Unsaved changes");

    clearTimeout(saveTimer);

    saveTimer = setTimeout(() => {
        saveFile();
    }, AUTOSAVE_DELAY);
}


async function saveFile() {

    if (!currentFilePath) {
        setStatus("No file selected", "error");
        return false;
    }

    clearTimeout(saveTimer);

    if (saveInProgress) {

        saveAgain = true;

        return savePromise;
    }

    saveInProgress = true;

    savePromise = (async () => {

        let success = true;

        do {

            saveAgain = false;

            const pathToSave = currentFilePath;

            const versionToSave = editVersion;

            const contentToSave = editor.value;

            setStatus("Saving...");

            try {

                const result = await apiRequest("/api/files/save", {
                    method: "POST",
                    body: JSON.stringify({
                        path: pathToSave,
                        content: contentToSave
                    })
                });

                savedVersion = Math.max(savedVersion, versionToSave);

                if (editVersion > versionToSave) {

                    saveAgain = true;

                } else {

                    const git = result.git;

                    if (git.committed) {

                        setStatus(
                            `Saved and committed (${git.commit_hash.slice(0, 7)})`,
                            "saved"
                        );

                    } else {

                        setStatus("Saved - no Git changes", "saved");
                    }
                }

            } catch (error) {

                setStatus(`Save failed: ${error.message}`, "error");

                success = false;

                break;
            }

        } while (saveAgain);

        return success;

    })();

    try {

        return await savePromise;

    } finally {

        saveInProgress = false;

        savePromise = null;
    }
}


async function createNewFile() {

    if (!currentDirectory) {
        setStatus("Load a directory first", "error");
        return;
    }

    if (currentFilePath && editVersion > savedVersion) {

        const saved = await saveFile();

        if (!saved) {
            setStatus("Save failed. New file not created.", "error");
            return;
        }
    }

    const filename = prompt("Enter the new filename:");

    if (!filename || !filename.trim()) {
        return;
    }

    try {

        setStatus("Creating file...");

        const result = await apiRequest("/api/files/create", {
            method: "POST",
            body: JSON.stringify({
                directory: currentDirectory,
                filename: filename.trim(),
                content: ""
            })
        });

        await loadDirectory(currentDirectory);

        await openFile(result.path);

        setStatus("File created and committed", "saved");

    } catch (error) {

        setStatus(error.message, "error");
    }
}


async function initializeGit() {

    if (!currentDirectory) {
        setStatus("Load a directory first", "error");
        return;
    }

    try {

        setStatus("Initializing Git...");

        const result = await apiRequest("/api/git/init", {
            method: "POST",
            body: JSON.stringify({
                directory: currentDirectory
            })
        });

        if (result.initialized) {

            setStatus("Git repository initialized", "saved");

        } else {

            setStatus("Existing Git repository detected", "saved");
        }

    } catch (error) {

        setStatus(error.message, "error");
    }
}


async function loadGitHistory() {

    if (!currentFilePath) {
        setStatus("Open a file first", "error");
        return;
    }

    try {

        setStatus("Loading Git history...");

        const result = await apiRequest("/api/git/history", {
            method: "POST",
            body: JSON.stringify({
                path: currentFilePath,
                limit: 20
            })
        });

        historyList.replaceChildren();

        if (result.history.length === 0) {

            const message = document.createElement("p");

            message.className = "empty-message";
            message.textContent = "No commit history found for this file.";

            historyList.appendChild(message);

        } else {

            result.history.forEach(commit => {

                const item = document.createElement("div");

                item.className = "history-item";

                const message = document.createElement("strong");

                message.textContent = commit.message;

                const details = document.createElement("span");

                details.textContent =
                    `${commit.short_hash} | ${commit.author} | ${new Date(commit.date).toLocaleString()}`;

                item.appendChild(message);
                item.appendChild(details);

                historyList.appendChild(item);
            });
        }

        historyPanel.hidden = false;

        setStatus("Git history loaded", "saved");

    } catch (error) {

        setStatus(error.message, "error");
    }
}


editor.addEventListener("input", () => {

    updateCharacterCount();

    scheduleAutosave();
});


loadDirectoryBtn.addEventListener("click", () => {
    loadDirectory();
});


refreshFilesBtn.addEventListener("click", () => {
    loadDirectory();
});


newFileBtn.addEventListener("click", () => {
    createNewFile();
});


saveFileBtn.addEventListener("click", () => {
    saveFile();
});


initGitBtn.addEventListener("click", () => {
    initializeGit();
});


historyBtn.addEventListener("click", () => {
    loadGitHistory();
});


closeHistoryBtn.addEventListener("click", () => {
    historyPanel.hidden = true;
});


directoryInput.addEventListener("keydown", event => {

    if (event.key === "Enter") {
        loadDirectory();
    }
});


document.addEventListener("keydown", event => {

    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {

        event.preventDefault();

        if (!editor.disabled) {
            saveFile();
        }
    }
});


updateCharacterCount();
setStatus("Ready");
