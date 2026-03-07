import sqlite3
import uuid

DB_FILE = "/data/rules.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            rule_id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            metric TEXT NOT NULL,
            operator TEXT NOT NULL,
            threshold_value REAL NOT NULL,
            actuator_name TEXT NOT NULL,
            target_state TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Rule database initialized.", flush=True)
    removed = dedupe_rules()
    if removed:
        print(f"Removed {removed} duplicate rule(s).", flush=True)


def add_rule(source_name, metric, operator, threshold_value, actuator_name, target_state):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rule_id FROM rules
        WHERE source_name = ? AND metric = ? AND operator = ?
          AND threshold_value = ? AND actuator_name = ? AND target_state = ?
        LIMIT 1
    """, (source_name, metric, operator, threshold_value, actuator_name, target_state))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    rule_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO rules (
            rule_id, source_name, metric, operator, threshold_value, actuator_name, target_state
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (rule_id, source_name, metric, operator, threshold_value, actuator_name, target_state))

    conn.commit()
    conn.close()
    return rule_id


def get_rules_by_source_and_metric(source_name, metric):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM rules
        WHERE source_name = ? AND metric = ?
    """, (source_name, metric))

    rules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rules


def get_all_rules():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rules")
    rules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rules


def dedupe_rules():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM rules
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM rules
            GROUP BY source_name, metric, operator, threshold_value, actuator_name, target_state
        )
    """)

    removed = cursor.rowcount if cursor.rowcount != -1 else 0
    conn.commit()
    conn.close()
    return removed


def seed_demo_rules():
    """
    Add a couple of demo rules only if the table is empty.
    """
    existing = get_all_rules()
    if existing:
        print("Rules already exist, skipping demo seed.", flush=True)
        return

    add_rule(
        source_name="greenhouse_temperature",
        metric="temperature_c",
        operator=">",
        threshold_value=24.0,
        actuator_name="cooling_fan",
        target_state="ON"
    )

    add_rule(
        source_name="water_tank_level",
        metric="level_pct",
        operator="<",
        threshold_value=75.0,
        actuator_name="hall_ventilation",
        target_state="OFF"
    )

    print("Demo rules inserted.", flush=True)
