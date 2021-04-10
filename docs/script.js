// Reverse the letters of the word

function reverseString()
{
	let inputString = document.getElementById('inputtext').value;
	let newString = "";
	
	for (let i = inputString.length - 1; i >=0; i--) {
		newString += inputString[i];
	}
	
	document.getElementById('outputtext').innerHTML = newString;
}

// 20 multiples of a number

function calculateMultiple()
{
	let inputDigit = document.getElementById('inputnumber').value;
	let increment = 1
	let result = "<table border=1>";
	
	for(let i=0; i<5; i++) {
		result += "<tr>";
		for(let j=0; j<4; j++){
			result += "<td>"+inputDigit*increment+++"</td>";
		}
		result += "</tr>";
	}
	result += "</table>";
	
	document.getElementById('outputnumber').innerHTML = result;
}

// Load president data

d3.text("https://raw.githubusercontent.com/charleyferrari/CUNY_DATA_608/master/module5/data/presidents.csv", function(data) {
    let csv = d3.csv.parseRows(data);

    let container = d3.select("table")
        .append("table")

		.selectAll("tr")
			.data(csv).enter()
			.append("tr")

		.selectAll("td")
			.data(function(d) {return d;}).enter()
			.append("td")
			.text(function(d) {return d;});
});

// Search president height and weight

function search_president(){
	
  let input, lower, table, tr, td, i;
  input = document.getElementById("inputtext2");
  lower = input.value.toLowerCase();
  table = document.getElementById("president_table");
  tr = table.getElementsByTagName("tr");

  for (i=1; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td") ; 
    for(j=0 ; j < td.length ; j++)
    {
      let td_data = td[j] ;
      if (td_data) {
        if (td_data.innerHTML.toLowerCase().indexOf(lower) > -1) {
          tr[i].style.display = "";
          break ; 
        } else {
          tr[i].style.display = "none";
        }
      } 
    }
  }
}
