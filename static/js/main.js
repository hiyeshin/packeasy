$(document).ready(){
	function ChangeColor(tableRow, highLight) {
				if (highLight) {
					tableRow.style.backgroundColor = '#dcfac9';
				} else {
					tableRow.style.backgroundColor = 'white';
				}
			}

			function DoNav(theUrl) {
				document.location.href = theUrl;
			}
}
