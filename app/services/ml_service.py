"""
Machine Learning service.

This module handles ML model training and prediction for product returns.
"""

import logging
import pickle
from typing import Tuple

import pandas as pd
import openpyxl
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

logger = logging.getLogger(__name__)


class MLService:
    """Service class for machine learning operations."""

    def __init__(self, config):
        """
        Initialize MLService.

        Args:
            config: Application configuration object
        """
        self.config = config
        # Handle both Flask config dict and config class
        self.model_path = config.get('MODEL_PICKLE_PATH') if hasattr(config, 'get') else config.MODEL_PICKLE_PATH
        self.feature_path = config.get('FEATURE_EXTRACTION_PATH') if hasattr(config, 'get') else config.FEATURE_EXTRACTION_PATH

    def train_model(self, file_path: str) -> bool:
        """
        Train logistic regression model on product returns data.

        Args:
            file_path (str): Path to Excel file with training data

        Returns:
            bool: True if training successful
        """
        try:
            # Parse Excel file
            sheets = self._parse_excel(file_path)
            fee_earnings = sheets.get('Fee_Earnings')

            if fee_earnings is None:
                raise ValueError("Fee-Earnings sheet not found")

            # Filter valid returns data
            valid_rows = pd.to_numeric(fee_earnings['Returns'], errors='coerce').notna()
            fee_earnings = fee_earnings[valid_rows].copy()
            fee_earnings['Returns'] = fee_earnings['Returns'].astype(int)

            product_names = fee_earnings['Name']
            product_returns = fee_earnings['Returns']

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                product_names,
                product_returns,
                test_size=0.2,
                random_state=3
            )

            # Feature extraction
            vectorizer = TfidfVectorizer(
                min_df=1,
                stop_words='english',
                lowercase=True
            )

            X_train_features = vectorizer.fit_transform(X_train)
            X_test_features = vectorizer.transform(X_test)

            # Train model
            model = LogisticRegression(max_iter=1000)
            model.fit(X_train_features, y_train)

            # Save model and vectorizer
            with open(self.model_path, 'wb') as f:
                pickle.dump(model, f)

            with open(self.feature_path, 'wb') as f:
                pickle.dump(vectorizer, f)

            # Log metrics
            self._log_metrics(model, X_train_features, X_test_features, y_train, y_test)

            logger.info("ML model trained and saved successfully")
            return True

        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise

    def predict_returns(self, file_path: str) -> bool:
        """
        Predict returns for products in product details file.

        Args:
            file_path (str): Path to product details Excel file

        Returns:
            bool: True if prediction successful
        """
        try:
            # Load model and vectorizer
            with open(self.model_path, 'rb') as f:
                model = pickle.load(f)

            with open(self.feature_path, 'rb') as f:
                vectorizer = pickle.load(f)

            # Read product details
            # Handle both Flask config dict and config class
            product_file = self.config.get('PRODUCT_DETAILS_FILE') if hasattr(self.config, 'get') else self.config.PRODUCT_DETAILS_FILE
            product_df = pd.read_excel(
                product_file,
                sheet_name="Product_details"
            )

            product_names = product_df['Product_Name']

            # Transform and predict
            features = vectorizer.transform(product_names)
            predictions = model.predict(features)

            product_df['result'] = predictions

            # Save results
            self._save_predictions(product_df)

            logger.info(f"Predictions completed for {len(product_df)} products")
            return True

        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise

    def _parse_excel(self, file_path: str) -> dict:
        """
        Parse Excel file and return sheets.

        Args:
            file_path (str): Path to Excel file

        Returns:
            dict: Dictionary of sheet_name -> dataframe
        """
        excel_file = pd.ExcelFile(file_path)
        sheets = {}

        for sheet_name in excel_file.sheet_names:
            sheet = excel_file.parse(sheet_name)
            sheet.columns = sheet.iloc[0]
            sheet = sheet[1:].reset_index(drop=True)
            normalized_name = sheet_name.replace("-", "_")
            sheets[normalized_name] = sheet

        return sheets

    def _log_metrics(
        self,
        model,
        X_train: any,
        X_test: any,
        y_train: pd.Series,
        y_test: pd.Series
    ) -> None:
        """
        Log model performance metrics.

        Args:
            model: Trained model
            X_train: Training features
            X_test: Test features
            y_train: Training labels
            y_test: Test labels
        """
        # Training metrics
        train_pred = model.predict(X_train)
        train_metrics = {
            'accuracy': accuracy_score(y_train, train_pred),
            'precision': precision_score(y_train, train_pred, zero_division=0),
            'recall': recall_score(y_train, train_pred, zero_division=0),
            'f1': f1_score(y_train, train_pred, zero_division=0)
        }

        logger.info("Training Set Metrics:")
        logger.info(f"  Accuracy: {train_metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {train_metrics['precision']:.4f}")
        logger.info(f"  Recall: {train_metrics['recall']:.4f}")
        logger.info(f"  F1 Score: {train_metrics['f1']:.4f}")

        # Test metrics
        test_pred = model.predict(X_test)
        test_metrics = {
            'accuracy': accuracy_score(y_test, test_pred),
            'precision': precision_score(y_test, test_pred, zero_division=0),
            'recall': recall_score(y_test, test_pred, zero_division=0),
            'f1': f1_score(y_test, test_pred, zero_division=0)
        }

        logger.info("Test Set Metrics:")
        logger.info(f"  Accuracy: {test_metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {test_metrics['precision']:.4f}")
        logger.info(f"  Recall: {test_metrics['recall']:.4f}")
        logger.info(f"  F1 Score: {test_metrics['f1']:.4f}")

    def _save_predictions(self, predictions_df: pd.DataFrame) -> None:
        """
        Save predictions to Excel file.

        Args:
            predictions_df (pd.DataFrame): Dataframe with predictions
        """
        # Handle both Flask config dict and config class
        file_path = self.config.get('PRODUCT_DETAILS_FILE') if hasattr(self.config, 'get') else self.config.PRODUCT_DETAILS_FILE

        # Check if Results sheet exists
        excel_file = pd.ExcelFile(file_path)
        has_results = 'Results' in excel_file.sheet_names

        if has_results:
            # Remove existing Results sheet
            workbook = openpyxl.load_workbook(file_path)
            if 'Results' in workbook.sheetnames:
                del workbook['Results']
            workbook.save(file_path)
            workbook.close()

        # Add new Results sheet
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
            predictions_df.to_excel(writer, sheet_name='Results', index=False)
