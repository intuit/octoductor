import React, { Component } from "react";
import Grid from "@material-ui/core/Grid";
import Typography from '@material-ui/core/Typography';
import Paper from "@material-ui/core/Paper";
import { makeStyles, withStyles } from '@material-ui/core/styles';
import clsx from 'clsx';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardMedia from '@material-ui/core/CardMedia';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import Collapse from '@material-ui/core/Collapse';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import IconButton from '@material-ui/core/IconButton';
import Avatar from '@material-ui/core/Avatar';
import { yellow, green, red, deepOrange, deepPurple } from '@material-ui/core/colors';

const useStyles = makeStyles((theme) => ({
    txtRow: {
        display: "flex",
        justifyContent: "flex-end",
    },
    root: {
        maxWidth: 345,
    },
    media: {
        height: 0,
        paddingTop: '56.25%', // 16:9
    },
    expand: {
        transform: 'rotate(0deg)',
        marginLeft: 'auto',
        transition: theme.transitions.create('transform', {
            duration: theme.transitions.duration.shortest,
        }),
    },
    expandOpen: {
        transform: 'rotate(180deg)',
    },
    orange: {
        color: theme.palette.getContrastText(deepOrange[500]),
        backgroundColor: deepOrange[500],
    },
    purple: {
        color: theme.palette.getContrastText(deepPurple[500]),
        backgroundColor: deepPurple[500],
    },
    avatar: {
        backgroundColor: deepOrange[500],
    },
    red: {
        color: theme.palette.getContrastText(red[500]),
        backgroundColor: red[500],
    },
    yellow: {
        color: theme.palette.getContrastText(yellow[500]),
        backgroundColor: yellow[500],
    },
    green: {
        color: theme.palette.getContrastText(green[500]),
        backgroundColor: green[500],
    },
    repoCols: {
        display: "flex",
    },
    repoInfo: {
        display: "flex",
        padding: "0 5px ",
        flexDirection: "column",
    }
}))

export default function RepoCard(props) {
    const classes = useStyles();
    const [expanded, setExpanded] = React.useState(false);

    const handleExpandClick = () => {
        setExpanded(!expanded);
    };

    let clr = 'red';
    if (props.repo.code_cov > 50) clr = 'yellow';
    if (props.repo.code_cov > 75) clr = 'green';

    return (
        <Grid key={props.repo._id} item xs={3}>
            <Card className={classes.root}>
                <CardHeader
                    avatar={
                        <Avatar aria-label="recipe" className={classes[clr]}>
                            {parseInt(props.repo.code_cov)}
                        </Avatar>
                    }
                    subheader="intuit"
                    title={props.repo.repoName}
                />
                <CardActions disableSpacing>
                    <IconButton
                        className={clsx(classes.expand, {
                            [classes.expandOpen]: expanded,
                        })}
                        onClick={handleExpandClick}
                        aria-expanded={expanded}
                        aria-label="show more"
                    >
                        <ExpandMoreIcon />
                    </IconButton>
                </CardActions>
                <Collapse in={expanded} timeout="auto" unmountOnExit>
                    <CardContent>
                        <div className={classes.repoCols}>
                            <div className={classes.repoInfo}>
                                <div className={classes.txtRow}>Owner: </div>
                                <div className={classes.txtRow}>Code Cov: </div>
                                <div className={classes.txtRow}>Lines of Code: </div>
                                <div className={classes.txtRow}>No. of Commits: </div>
                                <div className={classes.txtRow}>Language: </div>
                                <div className={classes.txtRow}>Contributors: </div>
                            </div>
                            <div className={classes.repoInfo}>
                                <div>{props.repo.owner}</div>
                                <div>{props.repo.code_cov}%</div>
                                <div>{props.repo.loc}</div>
                                <div>{props.repo.no_commits}</div>
                                <div>{props.repo.language}</div>
                                <div>{props.repo.contributors.length}</div>
                            </div>
                        </div>
                    </CardContent>

                </Collapse>
            </Card>
        </Grid>
    )
}
