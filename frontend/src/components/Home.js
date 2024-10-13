import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../UserContext';
import UserProfile from "./UserProfile";
import PartsTable from "./PartsTable";
import AircraftTable from "./AircraftTable";

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
                    {user.is_staff && user.is_superuser ? (
                        <h2>{'Admin Panel: /admin'}</h2>
                    ) : user.personnel.team.name === 'Assembly Team' ? (
                        <AircraftTable />
                    ) : (
                        <PartsTable />
                    )}
                </>
            )}
        </div>
    );
};

export default Home;
