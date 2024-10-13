import React, { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import axios from 'axios';
import AircraftCreateModal from './AircraftCreateModal';
import AircraftDetailModal from './AircraftDetailModal';
import { Button } from '@mui/material';

const AircraftTable = () => {
    const [aircrafts, setAircrafts] = useState([]);
    const [isCreateModalOpen, setCreateModalOpen] = useState(false);
    const [isDetailModalOpen, setDetailModalOpen] = useState(false);
    const [selectedAircraft, setSelectedAircraft] = useState(null);

    const fetchAircrafts = async () => {
        const token = localStorage.getItem('token');
        try {
            const response = await axios.get('/api/aircrafts/', {
                headers: { Authorization: `Token ${token}` },
            });
            setAircrafts(response.data);
        } catch (error) {
            console.error('Error fetching aircrafts:', error);
        }
    };

    useEffect(() => {
        fetchAircrafts();
    }, []);

    const columns = [
        { field: 'id', headerName: 'ID', width: 90 },
        { field: 'name', headerName: 'Name', width: 150 },
        { field: 'serial_number', headerName: 'Serial Number', width: 150 },
        { field: 'created_at', headerName: 'Created At', width: 150 },
        { field: 'is_produced', headerName: 'Is Produced', width: 150 },
        {
            field: 'action',
            headerName: 'Action',
            width: 150,
            renderCell: (params) => (
                <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleRowClick(params.row)}
                >
                    Detail
                </Button>
            ),
        },
    ];

    const handleRowClick = async (row) => {
        const token = localStorage.getItem('token');
        try {
            const response = await axios.get(`/api/aircrafts/${row.id}/`, {
                headers: { Authorization: `Token ${token}` },
            });
            console.log('Fetched aircraft details:', response.data);
            setSelectedAircraft(response.data);
            setDetailModalOpen(true);
        } catch (error) {
            console.error('Error fetching aircraft details:', error);
        }
    };

    const handleUpdate = () => {
        fetchAircrafts();
    };

    return (
        <div style={{ height: 400, width: '100%' }}>
            <h2>Aircrafts</h2>
            <Button variant="contained" color="primary" onClick={() => setCreateModalOpen(true)}>
                Create Aircraft
            </Button>
            <DataGrid
                rows={aircrafts}
                columns={columns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                disableSelectionOnClick
                onRowClick={(params) => handleRowClick(params.row)}
                getRowId={(row) => row.id}
                sx={{
                    marginTop: '20px',
                    '& .MuiDataGrid-cell': {
                        color: '#333',
                    },
                }}
            />
            <AircraftCreateModal isOpen={isCreateModalOpen} onClose={() => setCreateModalOpen(false)} onAircraftCreated={fetchAircrafts} />
            <AircraftDetailModal isOpen={isDetailModalOpen} onClose={() => setDetailModalOpen(false)} aircraft={selectedAircraft} onUpdate={handleUpdate} />
        </div>
    );
};

export default AircraftTable;
