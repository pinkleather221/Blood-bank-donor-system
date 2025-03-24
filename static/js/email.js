// Handle template selection
document.addEventListener('DOMContentLoaded', function() {
    // Template selection buttons
    const templateButtons = document.querySelectorAll('.use-template');
    templateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const templateName = this.getAttribute('data-template');
            loadEmailTemplate(templateName);
        });
    });

    // Tab switching
    const tabLinks = document.querySelectorAll('.nav-link');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            // Hide all tab panes
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // Show target tab pane
            document.querySelector(targetId).classList.add('show', 'active');
            
            // Update active tab
            tabLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Blood group selection
    const recipientTypeSelect = document.getElementById('recipient_type');
    const bloodGroupDiv = document.getElementById('blood_group_div');
    
    if (recipientTypeSelect && bloodGroupDiv) {
        recipientTypeSelect.addEventListener('change', function() {
            if (this.value === 'blood_group_donors') {
                bloodGroupDiv.style.display = 'block';
            } else {
                bloodGroupDiv.style.display = 'none';
            }
        });
    }
});

function loadEmailTemplate(templateName) {
    fetch(`/load-template/?template=${templateName}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('subject').value = data.subject;
            document.getElementById('message').value = data.message;
            
            // Switch to compose tab
            document.querySelector('a[href="#compose"]').click();
        })
        .catch(error => {
            console.error('Error loading template:', error);
        });
}