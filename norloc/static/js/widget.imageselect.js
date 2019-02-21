document.addEventListener('DOMContentLoaded', function() { 
	// ImageSelect
	var imageselects = document.getElementsByClassName('imageselect');
    
	for(var i = 0; i < imageselects.length; i++) {
		// Properties
		var imageselect = imageselects[i];
		var imageselect_label = imageselect.querySelector('label');
		var imageselect_id = imageselect_label.getAttribute('for');
		var imageselect_preview = imageselect.querySelector('img');
		var imageselect_input = imageselect.querySelector('input#'+imageselect_id);
		var imageselect_srcinitial = imageselect_preview.getAttribute('src');
		var imageselect_srccleared = imageselect_input.getAttribute('srccleared');
		var imageselect_clear = imageselect.querySelector('input[type="checkbox"]');

		// Update preview
		imageselect_input.addEventListener('change', function(e) {
			if (this.files && this.files[0]) {
				var reader = new FileReader();

				reader.onload = function(e) {
					imageselect_preview.setAttribute('src', e.target.result)
					imageselect.classList.remove('cleared');
					if (imageselect_clear) {
						imageselect_clear.checked = false;
					}
				}

				reader.readAsDataURL(this.files[0]);
			}
		});

		// Clear
		if (imageselect_clear) {
			imageselect.querySelector('.imageselect-btn.clear').addEventListener('click', function(e) {
				imageselect_clear.checked = !imageselect_clear.checked;

				if (imageselect_clear.checked) {
					imageselect.classList.add('cleared');
					imageselect_input.value = '';
					if (imageselect_srccleared) {
						imageselect_preview.setAttribute('src', imageselect_srccleared);
					}
				} else {
					imageselect.classList.remove('cleared');
					if (imageselect_srcinitial) {
						imageselect_preview.setAttribute('src', imageselect_srcinitial);
					}
				}
			});
		}
	}
}, false);