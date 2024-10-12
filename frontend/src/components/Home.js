import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../UserContext';
import UserProfile from "./UserProfile";
import PartsTable from "./PartsTable";

const Home = () => {
    const { user } = useUser();
    const navigate = useNavigate();

    useEffect(() => {
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    return (
        <div>
            {user && (
                <>
                    <UserProfile user={user}/>
                    <PartsTable />
                </>
            )}
        </div>
    );
};

export default Home;
