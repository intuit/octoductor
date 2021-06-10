import React, { Component } from "react";
import './App.css';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import Link from '@material-ui/core/Link';
import CircleChart from "./components/CircleChart";
import SecondChart from "./components/SecondChart";
import { dataSet } from "./data/repos"
import { withStyles } from '@material-ui/core/styles';
import Grid from "@material-ui/core/Grid";
import RepoCard from "./components/RepoCard";

const Copyright = () =>
  <Typography variant="body2" color="textSecondary" align="center">
    {'Copyright © '}
    <Link color="inherit" href="https://material-ui.com/">
      Intuit - AI
      </Link>{' '}
    {new Date().getFullYear()}
    {'.'}
  </Typography>


const useStyles = (theme) => ({
  root: {
    flexGrow: 1,
    backgroundColor: "#f5f5f5",
    padding: "20px"
  },
  outline: {
    border: "1px solid blue"
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
});
class App extends Component {
  constructor(props) {
    super(props);
    this.dataSet = dataSet;
    this.state = { repos_of_interest: [] }
    this.setReposOfInterest = this.setReposOfInterest.bind(this);
  }

  getRepos(repos){
    return repos.map(r => <RepoCard repo={r}/>)
  }
  setReposOfInterest(r) {
    this.setState({ repos_of_interest: r })
    // if (r && r.length) console.log(r)
  }
  render() {
    const { classes } = this.props;
    // console.log(this.state.repos_of_interest)
    return (
      <Grid spacing={3} className={classes.root} sm={12} container>
        <Grid spacing={3} sm={12} container>
          <Grid item xs={4} >
            <CircleChart
              count={this.dataSet.filter(x => x.hasAssetYML).length}
              color={'darkred'}
              total={this.dataSet.length}
            >
              <div>Repos contain <i>asset.yml</i></div>
            </CircleChart>
          </Grid>
          <Grid item xs={4} >
            <CircleChart
              count={89}
              color={'darkgreen'}
              total={100}
            >
              <div>Avg. Test Coverage</div>
            </CircleChart>
          </Grid>
          <Grid item xs={4} >
            <CircleChart
              count={6}
              color={'darkblue'}
              total={8}
            >
              <div>Median no. of <i>onboarded</i> repositories</div>
            </CircleChart>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <SecondChart data={this.dataSet} setRepos={this.setReposOfInterest} />
        </Grid>
        <Grid container spacing={2} xs={12}>
          { this.getRepos(this.state.repos_of_interest) }
        </Grid>
        <Grid item xs={12}>
          <Box my={4}>
            <Typography align="center" variant="h4" component="h1" gutterBottom>
              octoductor <i>Dashboard</i>
            </Typography>
            <Copyright />
          </Box>
        </Grid>
      </Grid>
    );
  }
}

export default withStyles(useStyles)(App);
