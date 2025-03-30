function downloadCV(event) {
    event.preventDefault(); // Prevent the default action of the link
    
    var proceed = confirm("You need a reason for downloading the cv, do you want to proceed?");
    
    if (proceed) {
        // Second prompt with the options
        var reason = prompt("Please select the reason for downloading the CV:\n1. Recruiting\n2. Networking");

        // Handle the selected option
        switch(reason) {
            case '1':
                reason = 'Recruiting';
                break;
            case '2':
                reason = 'Networking';
                break;
            default:
                alert("You must select a valid option to download the CV.");
                return downloadCV(event);
        }
    }

    // Check if the user entered a valid reason
    if (reason && reason.trim() !== "") {
        // Create a new link element to download the file
        var link = document.createElement('a');
        link.href = '/pdf/Mohamad_Arouni_CV.pdf'; // Path to your CV file
        link.download = 'Mohamad_Arouni_CV.pdf'; // Name for the downloaded file

        // Programmatically click the link to trigger the download
        link.click();
        
        return reason; // Return the reason provided by the user
    } 

    return null; // Return null if no valid reason was provided
}

// Attach the downloadCV function to the download button after the document is loaded
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('downloadButton').addEventListener('click', downloadCV);
});
