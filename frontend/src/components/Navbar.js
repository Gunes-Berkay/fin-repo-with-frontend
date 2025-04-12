import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import AppBar from '@mui/material/AppBar';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import {Link, useLocation} from 'react-router-dom'
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import MainPage from './MainPage';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import WalletIcon from '@mui/icons-material/Wallet';
import NewspaperIcon from '@mui/icons-material/Newspaper';
import WaterfallChartIcon from '@mui/icons-material/WaterfallChart';
import { IconButton } from '@mui/material';

const drawerWidth = 240;

export default function ClippedDrawer(props) {
    const location = useLocation()
    const path = location.pathname
    const {drawerWidth, content} = props

    const [open, setOpen] = React.useState(false)
    const changeOpenStatus = () =>  {
      setOpen(!open)
    }
    const myDrawer = (
      <div>
         <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            
              <ListItem  disablePadding>
                <ListItemButton component={Link} to='' selected={"" === path}>
                  <ListItemIcon>
                    <HomeIcon/>
                  </ListItemIcon>
                  <ListItemText primary={"MainPage"} />
                </ListItemButton>
              </ListItem>

              <ListItem  disablePadding>
                <ListItemButton component={Link} to='/wallet' selected={"" === path}>
                  <ListItemIcon>
                    <WalletIcon/>
                  </ListItemIcon>
                  <ListItemText primary={"Wallet"} />
                </ListItemButton>
              </ListItem>

              <ListItem  disablePadding>
                <ListItemButton component={Link} to='/charts' selected={"" === path}>
                  <ListItemIcon>
                    <WaterfallChartIcon/>
                  </ListItemIcon>
                  <ListItemText primary={"Charts"} />
                </ListItemButton>
              </ListItem>

              <ListItem  disablePadding>
                <ListItemButton component={Link} to='/news' selected={"" === path}>
                  <ListItemIcon>
                    <NewspaperIcon/>
                  </ListItemIcon>
                  <ListItemText primary={"News"} />
                </ListItemButton>
              </ListItem>
            
          </List>
         
        </Box>
      </div>
    )
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>

          <IconButton onClick={changeOpenStatus}>
            <MenuIcon/>
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Clipped drawer
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open = {open}
        onClose={changeOpenStatus}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
      >
        {myDrawer}
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
          {content}
      </Box>
    </Box>
  );
}