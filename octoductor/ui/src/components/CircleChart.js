import React, {Component} from "react";
import * as d3 from "d3";
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';


const useStyles = (theme) => ({
    paper: {
      padding: theme.spacing(2),
      textAlign: 'center',
      color: theme.palette.text.secondary,
    },
  });
class CircleChart extends Component {
    constructor(props){
        super(props);
        this.myRef = React.createRef();
    }
    componentDidMount(){
        const size = 300;
        const result = percentToRadians(this.props.count/ this.props.total);

        const svg = d3.select(this.myRef.current)
                        .append('svg')
                        .attr('width', size)
                        .attr('height', size)
                        .append('g')
                        .attr("transform", `translate(${size/2},${size/2})`)


        const arc = d3.arc()
                        .innerRadius((d, i) => (size/2)*.7)
                        .outerRadius((d, i) => (size/2))
                        .startAngle(0)
                        .endAngle(result )

        svg.append('path')
            .attr('class', 'arc')
            .attr('d',arc)
            .style('fill',this.props.color);

        svg.append("g")
            .attr("class", "focus-g")
            .attr("text-anchor", "middle")
            .attr("fill", "black")
            .append('text')
            .style("font-size",'52pt')
            .text(this.props.count)
            .attr('y','20')

    }

    render(){
        const {classes} = this.props;
        return (
            <Paper className={classes.paper}>
                <div ref={this.myRef}></div>
                {this.props.children}
            </Paper>
        )
    }
}
const percentToDegrees = percent => (percent)*360
const degreesToRadians = degs => ( Math.PI/180 ) * degs
const percentToRadians = per => degreesToRadians(percentToDegrees(per))

export default withStyles(useStyles)(CircleChart);