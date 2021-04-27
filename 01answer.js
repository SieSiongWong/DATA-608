// DATA 608 - Assignment #6
// Sie Siong Wong
// Date: 04-26-2021

d3.csv('ue_industry.csv', data => {

    // Define your scales and generator here.
	const xScale = d3.scaleLinear()
		.domain(d3.extent(data, d => +d.index))
		.range([20, 1180]);
		
	const yScale = d3.scaleLinear()
		.domain(d3.extent(data, d => +d.Agriculture))
		.range([580, 20]);

	const line = d3.line()
		.x(d => xScale(+d.index))
		.y(d => yScale(+d.Agriculture));

	// append more elements here
    d3.select('#answer1')
        .append('path')
		.attr('d', line(data))
		.attr('stroke', '#474a4f');
		

});
