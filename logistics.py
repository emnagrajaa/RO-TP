import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFileDialog, QGroupBox, QSplitter,
    QHeaderView, QTabWidget, QTextEdit, QScrollArea,
    QFrame
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor
from gurobipy import Model, GRB
import csv

class StyledSpinBox(QSpinBox):
    """SpinBox personnalisé avec un meilleur style"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 12px;
                color: #000000;
            }
        """)

class StyledButton(QPushButton):
    """Bouton personnalisé"""
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.setMinimumHeight(30)

class TransportApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📦 Solveur de Problème de Transport")
        self.initUI()
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #000000;
            }
            QLabel {
                font-size: 11px;
                color: #000000;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
                color: #000000;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #000000;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #eee;
                font-size: 11px;
                color: #000000;
            }
            QTableWidget::item {
                padding: 4px;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #f8f8f8;
                padding: 4px;
                border: 1px solid #eee;
                font-weight: bold;
                color: #000000;
            }
            QTextEdit {
                color: #000000;
            }
            QSpinBox {
                color: #000000;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Titre principal
        title_label = QLabel("🔧 Solveur de Problème de Transport avec Gurobi")
        title_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #000000;
            margin: 10px 0;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Configuration de base
        config_group = QGroupBox("Configuration du Problème")
        config_layout = QHBoxLayout()
        
        # Section usines
        usines_group = QGroupBox("Usines (Sources)")
        usines_layout = QVBoxLayout()
        usine_label = QLabel("Nombre d'usines :")
        usine_label.setStyleSheet("color: #000000;")
        usines_layout.addWidget(usine_label)
        self.spin_usines = StyledSpinBox()
        self.spin_usines.setMinimum(1)
        self.spin_usines.setMaximum(10)
        self.spin_usines.setValue(3)
        usines_layout.addWidget(self.spin_usines)
        usines_group.setLayout(usines_layout)
        
        # Section entrepôts
        entrepots_group = QGroupBox("Entrepôts (Destinations)")
        entrepots_layout = QVBoxLayout()
        entrepot_label = QLabel("Nombre d'entrepôts :")
        entrepot_label.setStyleSheet("color: #000000;")
        entrepots_layout.addWidget(entrepot_label)
        self.spin_entrepots = StyledSpinBox()
        self.spin_entrepots.setMinimum(1)
        self.spin_entrepots.setMaximum(10)
        self.spin_entrepots.setValue(3)
        entrepots_layout.addWidget(self.spin_entrepots)
        entrepots_group.setLayout(entrepots_layout)
        
        config_layout.addWidget(usines_group)
        config_layout.addWidget(entrepots_group)
        config_layout.addStretch()
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.btn_create_tables = StyledButton("🔄 Générer les tableaux de données")
        self.btn_create_tables.clicked.connect(self.create_tables)
        self.btn_create_tables.setToolTip("Créer les tableaux pour saisir les données du problème")
        
        self.btn_solve = StyledButton("⚡ Résoudre le problème")
        self.btn_solve.clicked.connect(self.solve_transport)
        self.btn_solve.setEnabled(False)
        self.btn_solve.setToolTip("Résoudre le problème de transport avec Gurobi")
        
        self.btn_export = StyledButton("📊 Exporter les résultats")
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_export.setEnabled(False)
        self.btn_export.setToolTip("Exporter les résultats au format CSV")
        
        self.btn_reset = StyledButton("🗑️ Réinitialiser")
        self.btn_reset.clicked.connect(self.reset_all)
        self.btn_reset.setToolTip("Réinitialiser tous les champs")
        
        buttons_layout.addWidget(self.btn_create_tables)
        buttons_layout.addWidget(self.btn_solve)
        buttons_layout.addWidget(self.btn_export)
        buttons_layout.addWidget(self.btn_reset)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)

        # Zone principale avec splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panneau gauche : Données d'entrée dans une ScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        left_panel = QWidget()
        self.left_layout = QVBoxLayout(left_panel)
        self.left_layout.setSpacing(10)
        
        # Label initial
        self.data_label = QLabel("<center><i>Cliquez sur 'Générer les tableaux' pour créer les champs de saisie</i></center>")
        self.data_label.setStyleSheet("color: #666666; padding: 20px; text-align: center;")
        self.left_layout.addWidget(self.data_label)
        
        scroll_area.setWidget(left_panel)
        
        # Panneau droit : Résultats
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Onglets pour les résultats
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                color: #000000;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
                color: #000000;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Onglet des résultats
        results_tab = QWidget()
        results_tab_layout = QVBoxLayout(results_tab)
        
        # Informations de la solution
        self.solution_info = QTextEdit()
        self.solution_info.setReadOnly(True)
        self.solution_info.setMaximumHeight(100)
        self.solution_info.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 5px;
                font-size: 11px;
                color: #000000;
            }
        """)
        info_label = QLabel("Informations de la solution :")
        info_label.setStyleSheet("color: #000000; font-weight: bold;")
        results_tab_layout.addWidget(info_label)
        results_tab_layout.addWidget(self.solution_info)
        
        # Tableau des résultats dans une ScrollArea
        results_label = QLabel("Flux optimaux :")
        results_label.setStyleSheet("color: #000000; font-weight: bold; margin-top: 10px;")
        results_tab_layout.addWidget(results_label)
        
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        self.table_results = QTableWidget()
        self.table_results.setMinimumHeight(250)
        results_scroll.setWidget(self.table_results)
        results_tab_layout.addWidget(results_scroll)
        
        self.tab_widget.addTab(results_tab, "📊 Résultats")
        
        # Onglet des statistiques
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 5px;
                font-size: 11px;
                color: #000000;
            }
        """)
        stats_layout.addWidget(QLabel("<center><h3>Statistiques du problème</h3></center>"))
        stats_layout.addWidget(self.stats_text)
        self.tab_widget.addTab(stats_tab, "📈 Statistiques")
        
        right_layout.addWidget(self.tab_widget)
        
        # Ajouter les panneaux au splitter
        splitter.addWidget(scroll_area)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 700])
        
        main_layout.addWidget(splitter)
        
        # Barre de statut
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #e9ecef;
                border-top: 1px solid #dee2e6;
                color: #000000;
                font-size: 10px;
            }
        """)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def create_tables(self):
        try:
            m = self.spin_usines.value()
            n = self.spin_entrepots.value()
            
            # Supprimer le label initial s'il existe
            if self.data_label:
                self.left_layout.removeWidget(self.data_label)
                self.data_label.deleteLater()
                self.data_label = None
            
            # Nettoyer le conteneur
            while self.left_layout.count():
                child = self.left_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Table des offres (capacités)
            supply_group = QGroupBox(f"Capacités des usines (m={m})")
            supply_group.setStyleSheet("color: #000000;")
            supply_layout = QVBoxLayout()
            supply_layout.setSpacing(5)
            
            supply_instruction = QLabel("Saisir les capacités de production de chaque usine :")
            supply_instruction.setStyleSheet("color: #666666; font-size: 10px;")
            supply_layout.addWidget(supply_instruction)
            
            self.table_offres = QTableWidget(1, m)
            self.table_offres.setMinimumHeight(60)
            self.table_offres.setMaximumHeight(80)
            self.table_offres.setHorizontalHeaderLabels([f"Usine {i+1}" for i in range(m)])
            self.table_offres.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            # Configurer les cellules pour la saisie
            for i in range(m):
                item = QTableWidgetItem("100")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor("#000000"))
                item.setBackground(QColor(240, 248, 255))  # Bleu clair pour visibilité
                self.table_offres.setItem(0, i, item)
            
            supply_layout.addWidget(self.table_offres)
            supply_group.setLayout(supply_layout)
            self.left_layout.addWidget(supply_group)
            
            # Table des demandes
            demand_group = QGroupBox(f"Demandes des entrepôts (n={n})")
            demand_group.setStyleSheet("color: #000000;")
            demand_layout = QVBoxLayout()
            demand_layout.setSpacing(5)
            
            demand_instruction = QLabel("Saisir la demande de chaque entrepôt :")
            demand_instruction.setStyleSheet("color: #666666; font-size: 10px;")
            demand_layout.addWidget(demand_instruction)
            
            self.table_demandes = QTableWidget(1, n)
            self.table_demandes.setMinimumHeight(60)
            self.table_demandes.setMaximumHeight(80)
            self.table_demandes.setHorizontalHeaderLabels([f"Entrepôt {j+1}" for j in range(n)])
            self.table_demandes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            for j in range(n):
                item = QTableWidgetItem("100")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor("#000000"))
                item.setBackground(QColor(255, 240, 245))  # Rose clair pour visibilité
                self.table_demandes.setItem(0, j, item)
            
            demand_layout.addWidget(self.table_demandes)
            demand_group.setLayout(demand_layout)
            self.left_layout.addWidget(demand_group)
            
            # Table des coûts
            cost_group = QGroupBox(f"Coûts unitaires de transport (m×n = {m}×{n})")
            cost_group.setStyleSheet("color: #000000;")
            cost_layout = QVBoxLayout()
            cost_layout.setSpacing(5)
            
            cost_instruction = QLabel(f"Saisir les coûts de transport de chaque usine vers chaque entrepôt :")
            cost_instruction.setStyleSheet("color: #666666; font-size: 10px;")
            cost_layout.addWidget(cost_instruction)
            
            # Créer une ScrollArea pour le tableau des coûts
            cost_scroll = QScrollArea()
            cost_scroll.setWidgetResizable(True)
            cost_scroll.setMinimumHeight(200)
            cost_scroll.setMaximumHeight(400)
            cost_scroll.setStyleSheet("""
                QScrollArea {
                    border: 1px solid #ddd;
                    border-radius: 3px;
                }
                QScrollBar:vertical {
                    width: 12px;
                    background-color: #f5f5f5;
                }
                QScrollBar::handle:vertical {
                    background-color: #c1c1c1;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #a8a8a8;
                }
            """)
            
            self.table_costs = QTableWidget(m, n)
            self.table_costs.setHorizontalHeaderLabels([f"Entrepôt {j+1}" for j in range(n)])
            self.table_costs.setVerticalHeaderLabels([f"Usine {i+1}" for i in range(m)])
            self.table_costs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_costs.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            # Définir une taille minimale pour les lignes
            self.table_costs.verticalHeader().setDefaultSectionSize(40)
            
            # Remplir avec des valeurs par défaut
            for i in range(m):
                for j in range(n):
                    default_cost = (i + 1) * 10 + (j + 1)  # Valeurs variées
                    item = QTableWidgetItem(str(default_cost))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QColor("#000000"))
                    
                    # Ajouter une couleur de fond selon la valeur
                    if default_cost < 15:
                        item.setBackground(QColor(220, 255, 220))  # Vert clair
                    elif default_cost < 25:
                        item.setBackground(QColor(255, 255, 220))  # Jaune clair
                    else:
                        item.setBackground(QColor(255, 220, 220))  # Rouge clair
                    
                    self.table_costs.setItem(i, j, item)
            
            cost_scroll.setWidget(self.table_costs)
            cost_layout.addWidget(cost_scroll)
            cost_group.setLayout(cost_layout)
            self.left_layout.addWidget(cost_group)
            
            # Ajouter un stretch pour pousser tout vers le haut
            self.left_layout.addStretch()
            
            self.btn_solve.setEnabled(True)
            self.status_label.setText(f"Tableaux créés: {m} usines × {n} entrepôts - Prêt à saisir les données")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création des tableaux:\n{str(e)}")

    def solve_transport(self):
        try:
            m = self.spin_usines.value()
            n = self.spin_entrepots.value()
            
            # Lire les données
            supply = [float(self.table_offres.item(0, i).text()) for i in range(m)]
            demand = [float(self.table_demandes.item(0, j).text()) for j in range(n)]
            costs = [[float(self.table_costs.item(i, j).text()) for j in range(n)] for i in range(m)]
            
            # Vérifier l'équilibre offre-demande
            total_supply = sum(supply)
            total_demand = sum(demand)
            
            if abs(total_supply - total_demand) > 0.001:
                reply = QMessageBox.question(
                    self, "Problème déséquilibré",
                    f"Offre totale ({total_supply}) ≠ Demande totale ({total_demand}).\n"
                    "Voulez-vous continuer? (Un point fictif sera ajouté)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Modèle Gurobi
            self.status_label.setText("Résolution en cours...")
            QApplication.processEvents()
            
            model = Model("transport")
            model.setParam('OutputFlag', 0)  # Désactiver la sortie console
            
            x = {}
            for i in range(m):
                for j in range(n):
                    x[i, j] = model.addVar(lb=0, obj=costs[i][j], name=f"x_{i+1}_{j+1}")
            
            model.modelSense = GRB.MINIMIZE
            
            # Contraintes d'offre
            for i in range(m):
                model.addConstr(sum(x[i, j] for j in range(n)) <= supply[i], f"supply_{i}")
            
            # Contraintes de demande
            for j in range(n):
                model.addConstr(sum(x[i, j] for i in range(m)) >= demand[j], f"demand_{j}")
            
            model.optimize()
            
            if model.status == GRB.OPTIMAL:
                total_cost = model.objVal
                
                # Mettre à jour les informations de solution
                info_text = f"""
                <b>✓ SOLUTION OPTIMALE TROUVÉE !</b><br>
                <table style='border-collapse: collapse; margin: 5px 0;'>
                <tr><td style='padding: 2px;'><b>Coût total minimal:</b></td><td style='padding: 2px; color: green;'><b>{total_cost:.2f}</b></td></tr>
                <tr><td style='padding: 2px;'>Nombre de variables:</td><td style='padding: 2px;'>{m * n}</td></tr>
                <tr><td style='padding: 2px;'>Nombre de contraintes:</td><td style='padding: 2px;'>{m + n}</td></tr>
                <tr><td style='padding: 2px;'>Temps de résolution:</td><td style='padding: 2px;'>{model.Runtime:.2f}s</td></tr>
                <tr><td style='padding: 2px;'>Gap d'optimalité:</td><td style='padding: 2px;'>{model.MIPGap if hasattr(model, 'MIPGap') else 0:.2%}</td></tr>
                </table>
                """
                self.solution_info.setHtml(info_text)
                
                # Afficher tableau des résultats
                self.table_results.setRowCount(m + 2)
                self.table_results.setColumnCount(n + 2)
                
                # En-têtes
                headers = [f"E{j+1}" for j in range(n)] + ["Offre", "Coût usine"]
                self.table_results.setHorizontalHeaderLabels(headers)
                vertical_headers = [f"U{i+1}" for i in range(m)] + ["Demande", "Coût total"]
                self.table_results.setVerticalHeaderLabels(vertical_headers)
                
                # Remplir le tableau
                for i in range(m):
                    row_cost = 0.0
                    row_flow = 0.0
                    for j in range(n):
                        val = x[i, j].x
                        cost = costs[i][j] * val
                        row_cost += cost
                        row_flow += val
                        
                        item = QTableWidgetItem(f"{val:.2f}")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setForeground(QColor("#000000"))
                        
                        # Colorer les cellules avec flux > 0
                        if val > 0:
                            item.setBackground(QColor(220, 240, 255))
                        
                        self.table_results.setItem(i, j, item)
                    
                    # Colonne Offre
                    item = QTableWidgetItem(f"{row_flow:.2f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QColor("#000000"))
                    item.setBackground(QColor(240, 240, 240))
                    self.table_results.setItem(i, n, item)
                    
                    # Colonne Coût usine
                    item = QTableWidgetItem(f"{row_cost:.2f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QColor("#000000"))
                    item.setBackground(QColor(255, 245, 220))
                    self.table_results.setItem(i, n + 1, item)
                
                # Ligne Demande
                for j in range(n):
                    col_flow = sum(x[i, j].x for i in range(m))
                    item = QTableWidgetItem(f"{col_flow:.2f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QColor("#000000"))
                    item.setBackground(QColor(240, 240, 240))
                    self.table_results.setItem(m, j, item)
                
                # Cellules vides
                self.table_results.setItem(m, n, QTableWidgetItem(""))
                self.table_results.setItem(m, n + 1, QTableWidgetItem(""))
                
                # Ligne Coût total
                for j in range(n + 2):
                    if j == n + 1:  # Dernière cellule = coût total
                        item = QTableWidgetItem(f"{total_cost:.2f}")
                        item.setForeground(QColor("#000000"))
                        item.setBackground(QColor(220, 255, 220))
                    else:
                        item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table_results.setItem(m + 1, j, item)
                
                # Ajuster les colonnes
                self.table_results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                self.table_results.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                
                # Mettre à jour les statistiques
                self.update_stats(model, m, n, total_cost)
                
                self.btn_export.setEnabled(True)
                self.status_label.setText(f"✓ Solution optimale trouvée - Coût total: {total_cost:.2f}")
                
            else:
                QMessageBox.warning(self, "Aucune solution", 
                                  f"Statut: {model.status}\n"
                                  f"Aucune solution optimale trouvée.")
                self.status_label.setText("✗ Aucune solution optimale trouvée")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur de résolution", 
                               f"Une erreur est survenue:\n{str(e)}")
            self.status_label.setText("✗ Erreur lors de la résolution")

    def update_stats(self, model, m, n, total_cost):
        """Met à jour l'onglet des statistiques"""
        stats_text = f"""
        <h3 style='color: #000000;'>📊 STATISTIQUES DU PROBLÈME</h3>
        <hr style='border: 1px solid #ddd;'>
        
        <h4 style='color: #000000;'>Dimensions du problème :</h4>
        <ul style='color: #000000;'>
            <li>Nombre d'usines (sources): <b>{m}</b></li>
            <li>Nombre d'entrepôts (destinations): <b>{n}</b></li>
            <li>Total des variables: <b>{m * n}</b></li>
        </ul>
        
        <h4 style='color: #000000;'>Performance de résolution :</h4>
        <ul style='color: #000000;'>
            <li>Coût optimal: <b style='color: green;'>{total_cost:.2f}</b></li>
            <li>Temps de calcul: <b>{model.Runtime:.3f} secondes</b></li>
            <li>Nombre d'itérations: <b>{model.IterCount if hasattr(model, 'IterCount') else 'N/A'}</b></li>
            <li>Status: <b>{model.Status}</b></li>
        </ul>
        
        <h4 style='color: #000000;'>Informations techniques :</h4>
        <ul style='color: #000000;'>
            <li>Solveur: Gurobi Optimizer</li>
            <li>Méthode: Simplexe</li>
            <li>Variables: {model.numVars}</li>
            <li>Contraintes: {model.numConstrs}</li>
        </ul>
        """
        self.stats_text.setHtml(stats_text)

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer les résultats", 
            "transport_solution.csv", 
            "CSV Files (*.csv)"
        )
        if filename:
            try:
                with open(filename, "w", newline="", encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    
                    # En-tête avec métadonnées
                    writer.writerow(["Solution du Problème de Transport"])
                    writer.writerow([f"Généré le: {QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm:ss')}"])
                    writer.writerow([])
                    
                    # Résultats
                    n_cols = self.table_results.columnCount()
                    writer.writerow([self.table_results.horizontalHeaderItem(j).text() 
                                   for j in range(n_cols)])
                    
                    for i in range(self.table_results.rowCount()):
                        row_data = []
                        for j in range(n_cols):
                            item = self.table_results.item(i, j)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                    
                    writer.writerow([])
                    writer.writerow(["Informations supplémentaires:"])
                    writer.writerow([self.solution_info.toPlainText()[:100]])
                
                QMessageBox.information(
                    self, "Export réussi", 
                    f"Les résultats ont été exportés avec succès dans:\n{filename}"
                )
                self.status_label.setText(f"✓ Fichier exporté: {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'export", 
                                   f"Erreur lors de l'export:\n{str(e)}")

    def reset_all(self):
        """Réinitialise toute l'application"""
        reply = QMessageBox.question(
            self, "Réinitialiser", 
            "Voulez-vous vraiment tout réinitialiser?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Réinitialiser les spinboxes
            self.spin_usines.setValue(3)
            self.spin_entrepots.setValue(3)
            
            # Désactiver les boutons
            self.btn_solve.setEnabled(False)
            self.btn_export.setEnabled(False)
            
            # Nettoyer le panneau gauche
            while self.left_layout.count():
                child = self.left_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Réinitialiser les résultats
            self.table_results.clear()
            self.table_results.setRowCount(0)
            self.table_results.setColumnCount(0)
            self.solution_info.clear()
            self.stats_text.clear()
            
            # Message initial
            self.data_label = QLabel("<center><i>Cliquez sur 'Générer les tableaux' pour commencer la saisie des données</i></center>")
            self.data_label.setStyleSheet("color: #666666; padding: 20px; text-align: center;")
            self.left_layout.addWidget(self.data_label)
            
            self.status_label.setText("Prêt - Application réinitialisée")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TransportApp()
    window.setMinimumSize(1200, 800)
    window.show()
    
    sys.exit(app.exec())