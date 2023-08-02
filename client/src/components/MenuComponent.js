import React from 'react';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import useApiCall from '../hooks/useApiCall';

const MenuComponent = ({ anchorEl, handleClose, selectedBatchId }) => {
  const { downloadCsvReport } = useApiCall();

  const handleCsvReportBySourceAccount = () => {
    // Call the API for CSV report of Total amount of funds paid out per unique source account
    downloadCsvReport(selectedBatchId, 'source_account')
    handleClose();
  };

  const handleCsvReportByDunkinBranch = () => {
    // Call the API for CSV report of Total amount of funds paid out per Dunkin branch
    downloadCsvReport(selectedBatchId, 'branch')
    handleClose();
  };

  const handleCsvReportByBatchName = () => {
    // Call the API for CSV report of all payments metadata for a given batch name
    downloadCsvReport(selectedBatchId, 'payments')
    handleClose();
  };

  return (
    <Menu
      id="long-menu"
      anchorEl={anchorEl}
      keepMounted
      open={Boolean(anchorEl)}
      onClose={handleClose}
    >
      <MenuItem onClick={handleCsvReportBySourceAccount}>
        Get CVS report of Total amount of funds paid out per unique source account.
      </MenuItem>
      <MenuItem onClick={handleCsvReportByDunkinBranch}>
        Get CVS report of Total amount of funds paid out per Dunkin branch.
      </MenuItem>
      <MenuItem onClick={handleCsvReportByBatchName}>
        Get CSV report of all payments metadata for a given batch name.
      </MenuItem>
    </Menu>
  );
};

export default MenuComponent;
