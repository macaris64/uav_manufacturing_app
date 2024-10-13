import React, { useEffect, useState } from 'react';
import { Modal, Box, Button, Tabs, Tab, Typography } from '@mui/material';
import UAVDesign from './UAVDesign';
import axios from 'axios';

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 1000,
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
    borderRadius: '8px',
    display: 'flex',
};

const AircraftDetailModal = ({ isOpen, onClose, aircraft, onUpdate }) => {
    const [value, setValue] = useState(0);
    const [availableParts, setAvailableParts] = useState([]);
    const [currentAircraftParts, setCurrentAircraftParts] = useState([]);
    const [errorMessage, setErrorMessage] = useState('');

    const fetchAvailableParts = async () => {
        const token = localStorage.getItem('token');
        try {
            const response = await axios.get('/api/parts/', {
                headers: {
                Authorization: `Token ${token}`,
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                },
            });
            setAvailableParts(response.data);
        } catch (error) {
            console.error('Error fetching available parts:', error);
        }
    };

    useEffect(() => {
        fetchAvailableParts();
    }, []);

    useEffect(() => {
        if (aircraft) {
            setCurrentAircraftParts(aircraft.parts || []);
        }
    }, [aircraft]);

    const handleTabChange = (event, newValue) => {
        setValue(newValue);
    };

    const handleAddPart = async (part) => {
        const token = localStorage.getItem('token');
        const partExists = currentAircraftParts.some(p => p.name === part.name);
        if (partExists) {
            setErrorMessage(`Cannot add another ${part.name}. Only one part of this type can be added.`);
            return; // Prevent adding the part
        }
        const partExistsInCurrentAircraft = currentAircraftParts.some(p => p.id === part.id);
        if (partExistsInCurrentAircraft) {
            setErrorMessage(`Part ${part.name} is already installed on this aircraft.`);
            return; // Prevent adding the part
        }

        try {
            await axios.post('/api/aircraftparts/', {
                aircraft: aircraft.id,
                part: part.id,
            }, {
                headers: { Authorization: `Token ${token}` },
            });

            // Update the part's is_used status to true
            await axios.patch(`/api/parts/${part.id}/`, { is_used: true }, {
                headers: { Authorization: `Token ${token}` },
            });

            await fetchAvailableParts();

            const updatedPart = await axios.get(`/api/parts/${part.id}/`, {
                headers: { Authorization: `Token ${token}` },
            });

            setCurrentAircraftParts(prev => [...prev, updatedPart.data]);
            setErrorMessage('');
            onUpdate();
        } catch (error) {
            setErrorMessage('Error adding part: ' + (error.response ? error.response.data : error.message));
            console.error('Error adding part:', error);
        }
    };

    const handleRemovePart = async (part) => {
        const token = localStorage.getItem('token');
        try {
            // Find the AircraftPart object
            const response = await axios.get(`/api/aircraftparts/?part=${part.id}&aircraft=${aircraft.id}`, {
                headers: { Authorization: `Token ${token}` },
            });

            if (response.data && response.data.length > 0) {
                const aircraftPartId = response.data[0].id;

                // Remove the part from the aircraft
                await axios.delete(`/api/aircraftparts/${aircraftPartId}/`, {
                    headers: { Authorization: `Token ${token}` },
                });

                // Update the part's is_used status to false
                await axios.patch(`/api/parts/${part.id}/`, { is_used: false }, {
                    headers: { Authorization: `Token ${token}` },
                });

                await fetchAvailableParts();

                setCurrentAircraftParts(prev => prev.filter(p => p.id !== part.id));
                setErrorMessage('');
                onUpdate();
            } else {
                setErrorMessage('No matching AircraftPart found for the given part.');
                console.error('No matching AircraftPart found for the given part.');
            }
        } catch (error) {
            setErrorMessage('Error removing part: ' + (error.response ? error.response.data : error.message));
            console.error('Error removing part:', error.response ? error.response.data : error.message);
        }
    };

    return (
        <Modal
            open={isOpen}
            onClose={onClose}
            aria-labelledby="aircraft-detail-modal"
            aria-describedby="aircraft-details"
        >
            <Box sx={style}>
                <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    {aircraft ? <UAVDesign parts={currentAircraftParts} /> : <div>No UAV Data Available</div>}
                </div>

                <div style={{ flex: 1, padding: '20px' }}>
                    <h2 id="aircraft-detail-modal">Aircraft Details</h2>
                    {aircraft ? (
                        <div>
                            <p><strong>Name:</strong> {aircraft.name}</p>
                            <p><strong>Serial Number:</strong> {aircraft.serial_number}</p>
                            <p><strong>Created At:</strong> {new Date(aircraft.created_at).toLocaleDateString()}</p>
                            <p><strong>Is Produced:</strong> {aircraft.is_produced ? 'Yes' : 'No'}</p>
                            {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
                            <h3>Installed Parts</h3>
                            {currentAircraftParts.length > 0 ? (
                                <ul>
                                    {currentAircraftParts.map(part => (
                                        <li key={part.id}>
                                            {part.name} - {part.aircraft_type}
                                            <Button variant="outlined" onClick={() => handleRemovePart(part)}>Remove</Button>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>No parts installed.</p>
                            )}

                            {/* Tabs for part types */}
                            <Tabs value={value} onChange={handleTabChange} aria-label="part types">
                                <Tab label="Wings" />
                                <Tab label="Body" />
                                <Tab label="Tail" />
                                <Tab label="Avionics" />
                            </Tabs>

                            {/* Tab content */}
                            {value === 0 && (
                                <Typography component="div" role="tabpanel" hidden={value !== 0}>
                                    <h4>Available Wings</h4>
                                    {availableParts.filter(part => part.name === 'WING' && part.aircraft_type === aircraft.name && !part.is_used).map((part) => (
                                        <div key={part.id}>
                                            <span>{part.name}</span>
                                            <Button variant="outlined" onClick={() => handleAddPart(part)}>Add</Button>
                                        </div>
                                    ))}
                                </Typography>
                            )}
                            {value === 1 && (
                                <Typography component="div" role="tabpanel" hidden={value !== 1}>
                                    <h4>Available Body Parts</h4>
                                    {availableParts.filter(part => part.name === 'BODY' && part.aircraft_type === aircraft.name && !part.is_used).map((part) => (
                                        <div key={part.id}>
                                            <span>{part.name}</span>
                                            <Button variant="outlined" onClick={() => handleAddPart(part)}>Add</Button>
                                        </div>
                                    ))}
                                </Typography>
                            )}
                            {value === 2 && (
                                <Typography component="div" role="tabpanel" hidden={value !== 2}>
                                    <h4>Available Tail Parts</h4>
                                    {availableParts.filter(part => part.name === 'TAIL' && part.aircraft_type === aircraft.name && !part.is_used).map((part) => (
                                        <div key={part.id}>
                                            <span>{part.name}</span>
                                            <Button variant="outlined" onClick={() => handleAddPart(part)}>Add</Button>
                                        </div>
                                    ))}
                                </Typography>
                            )}
                            {value === 3 && (
                                <Typography component="div" role="tabpanel" hidden={value !== 3}>
                                    <h4>Available Avionic Parts</h4>
                                    {availableParts.filter(part => part.name === 'AVIONICS' && part.aircraft_type === aircraft.name && !part.is_used).map((part) => (
                                        <div key={part.id}>
                                            <span>{part.name}</span>
                                            <Button variant="outlined" onClick={() => handleAddPart(part)}>Add</Button>
                                        </div>
                                    ))}
                                </Typography>
                            )}
                        </div>
                    ) : (
                        <p>No aircraft details available.</p>
                    )}
                    <Button variant="contained" color="primary" onClick={onClose}>
                        Close
                    </Button>
                </div>
            </Box>
        </Modal>
    );
};

export default AircraftDetailModal;
