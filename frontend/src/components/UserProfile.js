import React from 'react';

const UserProfile = ({ user }) => {
    return (
        <div style={styles.profileContainer}>
            <img
                src={'https://i.pravatar.cc/300'}
                alt="Profile Avatar"
                style={styles.avatar}
            />
            <div style={styles.userInfo}>
                <h2>{user.username}</h2>
                <p>Team: {user.personnel.team.name ? user.personnel.team.name : 'No Team Assigned'}</p>
            </div>
        </div>
    );
};

const styles = {
    profileContainer: {
        display: 'flex',
        alignItems: 'center',
        padding: '20px',
        backgroundColor: '#f4f4f4',
        borderBottom: '1px solid #ddd',
        marginBottom: '20px',
        width: '100%'
    },
    avatar: {
        width: '80px',
        height: '80px',
        borderRadius: '50%',
        marginRight: '20px'
    },
    userInfo: {
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
    }
};

export default UserProfile;
