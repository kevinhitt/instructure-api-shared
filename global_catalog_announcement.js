document.addEventListener('DOMContentLoaded', function () {
    // Exclude execution on pages with "admin" in the URL
    if (!window.location.href.includes('admin') && !window.location.href.includes('pdi')) { // This announcement does not apply to Admin pages or PDI subcatalog
        var appHeader = document.getElementById('app-header');
        var appFooter = document.getElementById('app-footer');
        if (appHeader) {
            var noticeDiv = document.createElement('div');
            noticeDiv.style.position = 'fixed';
            noticeDiv.style.zIndex = '100000';
            noticeDiv.style.left = '0';
            noticeDiv.style.top= '0'; // change to .bottom for lower level warning*****
            noticeDiv.style.width = '100%';

            var alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert--danger alert-dismissible'; // Change "warning" to "danger" / "success" for day of alert (warning is for precaution / days leading up to alert)
            alertDiv.role = 'alert';

            var closeButton = document.createElement('button');
            closeButton.type = 'button';
            closeButton.className = 'close';
            closeButton.setAttribute('data-dismiss', 'alert');
            closeButton.setAttribute('aria-label', 'Close');
            closeButton.innerHTML = '<span aria-hidden="true">×</span>';

            var iconElement = document.createElement('i');
            iconElement.className = 'icon-warning';

            var strongElement = document.createElement('strong');
            strongElement.textContent = 'Payment System Outage'; // Replace this with lower level warning message "Upcoming Payment System Maintenance"
            var innerDiv = document.createElement('div');
            innerDiv.style.float = 'right';
            innerDiv.style.marginRight = '25px';
            innerDiv.innerHTML = 'Please note registration for paid courses will be unavailable during system maintenance on <strong><u>Thursday, July 13<sup>th</sup> from 8:00am - 4:00pm EST</u></strong>';

            alertDiv.appendChild(closeButton);
            alertDiv.appendChild(iconElement);
            alertDiv.appendChild(strongElement);
            alertDiv.appendChild(innerDiv);

            noticeDiv.appendChild(alertDiv);

            appHeader.prepend(noticeDiv); 
            // appFooter.append(noticeDiv);  // Change insertion to footer for lower level alert
        }
    }
});
