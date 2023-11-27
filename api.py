import xmlrpc.client
import logging

class OdooAPI:
    def __init__(self, base_url, db_name, username, password, logger=None):
        """
        Initialize the OdooAPI instance.

        Parameters:
        - base_url (str): The base URL of the Odoo server, including the scheme, e.g: https://odoo.example.org.
        - db_name (str): The name of the database to connect to.
        - username (str): The username for Odoo authentication.
        - password (str): The password or API Key for Odoo authentication.
        - logger (logging.Logger, optional): A logger instance. If None, a default logger is used.
        """

        self.base_url = base_url
        self.db_name = db_name
        self.username = username
        self.password = password
        self.uid = None  # User ID obtained after authentication
        self.common_proxy = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/common')
        self.models_proxy = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO) 

    def authenticate(self):
        """
        Authenticate the user against the Odoo server.

        This method sets the user ID (uid) if authentication is successful. It raises an exception
        if authentication fails or encounters an unexpected error.
        """
        if self.uid is not None:
            return 
        try:
            self.uid = self.common_proxy.authenticate(self.db_name, self.username, self.password, {})
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Authentication failed: {e.faultString}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication: {e}")
            raise

    def execute_kw(self, model, method, args):
        """
        Execute a method on the Odoo server for a given model.

        Parameters:
        - model (str): The model name on which to execute the method.
        - method (str): The method name to execute.
        - args (list): The arguments to pass to the method.

        Returns:
        The result of the Odoo method execution.

        Raises an exception if the Odoo API call fails.
        """
        if not self.uid:
            self.authenticate()
        try:
            return self.models_proxy.execute_kw(self.db_name, self.uid, self.password, model, method, args)
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Odoo API call failed: {e.faultString}")
            raise

    def create_record(self, model, values):
        """
        Create a record in the specified Odoo model.

        Parameters:
        - model (str): The model in which to create a record.
        - values (dict): The values for the new record.

        Returns:
        The ID of the created record.

        Raises an exception if the create operation fails.
        """
        try:
            record_id = self.execute_kw(model, 'create', [values])
            return record_id
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Create operation failed: {e.faultString}")
            raise

    def read_records(self, model, domain=None, fields=None, offset=0, limit=50, order="id desc"):
        """
        Read records from the specified Odoo model.

        Parameters:
        - model (str): The model from which to read records.
        - domain (list, optional): The domain criteria for filtering records.
        - fields (list, optional): The fields to fetch in the records.
        - offset (int, optional): The offset for pagination.
        - limit (int, optional): The maximum number of records to fetch.
        - order (str, optional): The sorting order of records.

        Returns:
        A list of dictionaries, each representing a record.

        Raises  exception if the read operation fails.
        """

        all_records = []
        total_records = 0
        while True:
            records = self.execute_kw(model, 'search_read', [domain or [], fields or [], offset, limit, order])
            if not records:
                self.logger.info("No records to retrieve.")
                break
            all_records.extend(records)
            offset += limit
            total_records += len(records)
        self.logger.info(f"Total records retrieved: {total_records}")
        return all_records

    def update_record(self, model, record_id, values):
        """
        Update a record in the specified Odoo model.

        Parameters:
        - model (str): The model containing the record.
        - record_id (int): The ID of the record to update.
        - values (dict): The values to update in the record.

        Raises an exception if the update operation fails.
        """

        try:
            self.execute_kw(model, 'write', [[record_id], values])
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Update operation failed: {e.faultString}")
            raise

    def delete_record(self, model, record_id):
        """
        Delete a record from the specified Odoo model.

        Parameters:
        - model (str): The model from which to delete the record.
        - record_id (int): The ID of the record to delete.

        Raises an exception if the delete operation fails.
        """
        
        try:
            self.execute_kw(model, 'unlink', [[record_id]])
        except xmlrpc.client.Fault as e:
            self.logger.error(f"Delete operation failed: {e.faultString}")
            raise
