// --- In-Browser Page Editing Functionality ---

/**
 * Polls to check if the Toast UI Editor library is loaded, then calls the callback.
 * This makes the script resilient to network latency and script loading order issues.
 * @param {function} callback The function to call once the editor is available.
 */
function waitForToastUI(callback) {
    if (window.toastui && window.toastui.Editor) {
        callback();
    } else {
        setTimeout(() => waitForToastUI(callback), 100);
    }
}

/**
 * Initializes all the logic for the in-browser page editor.
 */
function initializePageEditor() {
    const editButton = document.getElementById('edit-page-btn');
    const saveButton = document.getElementById('save-page-btn');
    const cancelButton = document.getElementById('cancel-edit-btn');
    const editorContainer = document.getElementById('editor-container');
    const editorElement = document.getElementById('markdown-editor-tui');
    const contentWrapper = document.querySelector('.md-content');

    let editorInstance = null; // To hold the Toast UI Editor instance
    let themeObserver = null;  // To hold the MutationObserver for theme changes

    if (!editButton || !editorContainer || !contentWrapper || !editorElement) {
        return;
    }

    const getPagePath = () => {
        const meta = document.querySelector('meta[name="page-source-path"]');
        return meta ? meta.getAttribute('content') : null;
    };

    /**
     * Synchronizes the editor's theme with the website's current theme.
     * This is done by re-creating the editor instance with the new theme,
     * as the library does not support dynamic theme switching on an existing instance.
     */
    const syncEditorTheme = () => {
        if (!editorInstance) return;

        // Preserve the current content
        const content = editorInstance.getMarkdown();

        // Get the target theme from the body attribute
        const currentScheme = document.body.getAttribute('data-md-color-scheme');
        const newTheme = currentScheme === 'slate' ? 'dark' : 'light';

        // Destroy the old instance
        editorInstance.destroy();

        // Create a new instance with the correct theme
        editorInstance = new toastui.Editor({
            el: editorElement,
            initialValue: content,
            previewStyle: 'vertical',
            height: '70vh',
            initialEditType: 'markdown',
            usageStatistics: false,
            theme: newTheme // Set the theme here
        });
    };

    /**
     * Sets up a MutationObserver to watch for theme changes on the body element.
     */
    const observeThemeChanges = () => {
        if (themeObserver) themeObserver.disconnect();

        themeObserver = new MutationObserver(syncEditorTheme);
        
        // Watch for changes on the 'data-md-color-scheme' attribute
        themeObserver.observe(document.body, {
            attributes: true,
            attributeFilter: ['data-md-color-scheme']
        });
    };

    const showEditor = (content) => {
        if (!editorInstance) {
            // Determine initial theme when creating for the first time
            const currentScheme = document.body.getAttribute('data-md-color-scheme');
            const initialTheme = currentScheme === 'slate' ? 'dark' : 'light';

            editorInstance = new toastui.Editor({
                el: editorElement,
                initialValue: content,
                previewStyle: 'vertical',
                height: '70vh',
                initialEditType: 'markdown',
                usageStatistics: false,
                theme: initialTheme // Set theme on creation
            });
        }
        contentWrapper.parentNode.insertBefore(editorContainer, contentWrapper.nextSibling);
        contentWrapper.style.display = 'none';
        editorContainer.style.display = 'block';

        // Start watching for theme changes
        observeThemeChanges();
    };

    const hideEditor = () => {
        // Stop observing theme changes to prevent memory leaks
        if (themeObserver) {
            themeObserver.disconnect();
            themeObserver = null;
        }

        contentWrapper.style.display = 'block';
        if (editorContainer.parentNode) {
            editorContainer.parentNode.removeChild(editorContainer);
        }
        if (editorInstance) {
            editorInstance.destroy();
            editorInstance = null;
        }
    };

    editButton.addEventListener('click', async () => {
        const path = getPagePath();
        if (!path) {
            alert('Error: Could not determine page source path.');
            return;
        }
        try {
            const response = await fetch(`http://127.0.0.1:5001/api/get-doc?path=${path}`);
            if (!response.ok) throw new Error(`Failed to fetch doc: ${response.statusText}`);
            const data = await response.json();
            showEditor(data.content);
        } catch (error) {
            alert(`Failed to load editor: ${error.message}`);
        }
    });

    saveButton.addEventListener('click', async () => {
        if (!editorInstance) return;

        saveButton.disabled = true;
        saveButton.textContent = 'Saving...';
        const path = getPagePath();
        const content = editorInstance.getMarkdown();

        try {
            const response = await fetch('http://127.0.0.1:5001/api/save-doc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path, content }),
            });
            if (!response.ok) throw new Error(`Failed to save doc: ${response.statusText}`);
            location.reload();
        } catch (error) {
            alert(`Failed to save page: ${error.message}`);
            saveButton.disabled = false;
            saveButton.textContent = 'Save Changes';
        }
    });

    cancelButton.addEventListener('click', () => {
        if (confirm("Are you sure? Any unsaved changes will be lost.")) {
            hideEditor();
        }
    });
}

// Wait for the DOM to be ready, then wait for ToastUI to be loaded.
const setupEditorEventListeners = () => {
    waitForToastUI(initializePageEditor);
};

document.addEventListener('DOMContentLoaded', setupEditorEventListeners);
document.addEventListener('page:loaded', setupEditorEventListeners); 