import React from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../UserContext';

const Navbar = () => {
    const { user, logout } = useUser(); // Destructure user and logout from UserContext

    return (
        <nav style={styles.nav}>
            <div style={styles.brand}>
                <Link to="/" style={styles.brandLink}>UAV Manufacturing</Link> {/* Brand link */}
            </div>
            <div style={styles.navLinks}>
                {user ? (
                    <>
                        <span>Welcome, {user.username}</span> {/* Welcome message for logged-in users */}
                        <button onClick={logout} style={styles.button}>Logout</button> {/* Logout button */}
                    </>
                ) : (
                    <>
                        <Link to="/login" style={styles.link}>Login</Link> {/* Link to login page */}
                        <Link to="/register" style={styles.link}>Register</Link> {/* Link to register page */}
                    </>
                )}
            </div>
        </nav>
    );
};

// Styles for the Navbar components
const styles = {
    nav: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px 20px',
        backgroundColor: '#333',
        color: '#fff',
    },
    brand: {
        fontSize: '24px',
        fontWeight: 'bold',
    },
    brandLink: {
        textDecoration: 'none',
        color: '#fff',
    },
    navLinks: {
        display: 'flex',
        gap: '15px',
    },
    link: {
        textDecoration: 'none',
        color: '#fff',
    },
    button: {
        backgroundColor: 'transparent',
        border: 'none',
        color: '#fff',
        cursor: 'pointer',
    },
};

export default Navbar;
