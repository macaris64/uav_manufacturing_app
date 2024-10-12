import React, { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import axios from 'axios';
import PartCreateModal from './PartCreateModal';
import { Button } from '@mui/material';

const PartsTable = () => {
    const [parts, setParts] = useState([]);
    const [isModalOpen, setModalOpen] = useState(false);
    const [selectedRows, setSelectedRows] = useState([]);

    // Fetch parts from the API
    const fetchParts = async () => {
        const token = localStorage.getItem('token');
        try {
            const response = await axios.get('/api/parts/', {
                headers: { Authorization: `Token ${token}` },
            });
            setParts(response.data);
        } catch (error) {
            console.error('Error fetching parts:', error);
        }
    };

    // Fetch parts when the component mounts
    useEffect(() => {
        fetchParts();
    }, []);

    // Define columns for the DataGrid
    const columns = [
        { field: 'id', headerName: 'ID', width: 90 },
        { field: 'name', headerName: 'Name', width: 150 },
        { field: 'aircraft_type', headerName: 'Aircraft Type', width: 150 },
        { field: 'created_at', headerName: 'Created At', width: 150 },
        { field: 'is_used', headerName: 'Is Used', width: 150 },
    ];

    // Handle recycling of selected parts
    const handleRecycle = async () => {
        const token = localStorage.getItem('token');
        try {
            await axios.post('/api/parts/bulk-delete/',
                { ids: selectedRows },
                { headers: { Authorization: `Token ${token}` } }
            );
            fetchParts(); // Refresh parts after deletion
            setSelectedRows([]); // Clear selection
        } catch (error) {
            console.error('Error deleting parts:', error);
            if (error.response && error.response.data) {
                alert(error.response.data); // Show error message
            }
        }
    };

    return (
        <div style={{ height: 400, width: '100%' }}>
            <h2>Your Team's Parts</h2>
            <Button variant="contained" color="primary" onClick={() => setModalOpen(true)}>
                Create Part
            </Button>
            {selectedRows.length > 0 && (
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleRecycle}
                    style={{ marginLeft: '10px' }}>
                    Recycle
                </Button>
            )}
            <PartCreateModal
                isOpen={isModalOpen}
                onClose={() => setModalOpen(false)}
                onPartCreated={fetchParts}
            />
            <DataGrid
                rows={parts}
                columns={columns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                disableSelectionOnClick
                checkboxSelection
                onRowSelectionModelChange={(newSelection) => {
                    setSelectedRows(newSelection); // Update selected rows
                }}
                getRowId={(row) => row.id}
                sx={{
                    marginTop: '20px',
                    '& .MuiDataGrid-cell': {
                        color: '#333',
                    },
                }}
            />
        </div>
    );
};

export default PartsTable;
