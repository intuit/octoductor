import React from "react";
import * as d3 from "d3";
import Paper from '@material-ui/core/Paper';

class SecondChart extends React.Component {
    constructor(props){
        super(props);
        this.myRef2 = React.createRef();
        
    }

    componentDidMount() {
        const height = 400;
        const width = 1000;
        const margin = ({top: 80, right: 50, bottom: 30, left: 40})

        const xAxis = g => g
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x))
            .call(g => g.select(".domain").remove())
            .call(g => g.append("text")
                .attr("x", width - margin.right)
                .attr("y", -4)
                .attr("fill", "#000")
                .attr("font-weight", "bold")
                .attr("text-anchor", "end")
                .text("Activity"))

        const yAxis = g => g
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y))
            .call(g => g.select(".domain").remove())
            .call(g => g.select(".tick:last-of-type text").clone()
                .attr("x", 4)
                .attr("text-anchor", "start")
                .attr("font-weight", "bold")
                    .text("Code Coverage"))

        const x = d3.scaleLinear()
                    .domain(d3.extent(this.props.data, d => d.no_commits)).nice()
                    .range([margin.left, width - margin.right])
                    
        const y = d3.scaleLinear()
                    .domain(d3.extent(this.props.data, d => d.code_cov)).nice()
                    .range([height - margin.bottom, margin.top])

        const svg = d3.select(this.myRef2.current)
                        .append('svg')
                        .attr('width', width)
                        .attr('height', height)
                        .property("value", []);

        const brush = d3.brush().on("start brush end", e => {
            // this.props.setRepos(svg.attr('value'))
            brushed(e,this.props.setRepos )
        });

        svg.append("g").call(xAxis);
        
        svg.append("g").call(yAxis);

        const dot = svg.append("g")
                        .attr("fill", "none")
                        .attr("stroke", "steelblue")
                        .attr("stroke-width", 1.5)
                    .selectAll("circle")
                    .data(this.props.data)
                    .join("circle")
                    .attr("transform", d => `translate(${x(d.no_commits)},${y(d.code_cov)})`)
                    .attr("r", 3);
        svg.call(brush);
        function brushed({selection}, setRepos) {
            let value = [];
            if (selection) {
                const [[x0, y0], [x1, y1]] = selection;
                value = dot
                .style("stroke", "gray")
                .filter(d => x0 <= x(d.no_commits) && x(d.no_commits) < x1 && y0 <= y(d.code_cov) && y(d.code_cov) < y1)
                .style("stroke", "steelblue")
                .data();

                const output = value.length >10 ? value.slice(10) : value;
                // if(output.length) console.log(output);
                setRepos(output)
            } else {
                dot.style("stroke", "steelblue");
            }
            svg.property("value", value).dispatch("input");
            }
    }
    render(){
        return (<Paper ref={this.myRef2}></Paper>)
    }
}

export default SecondChart;