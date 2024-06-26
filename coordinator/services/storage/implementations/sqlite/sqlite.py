import json
import os
import sqlite3
from typing import Tuple, List, TypeVar

from coordinator.services.storage.interfaces.istorage import IStorage
from shared.annotations.custom import UUID, FitnessScore
from shared.models.entities.individual import IndividualEntity
from shared.models.value_objects.individual import IndividualValue
from shared.utils.thread_safe import global_thread_safe

T = TypeVar('T')


class SqliteStorage(IStorage[T]):
    __SETUP_SCRIPT = 'setup.sql'

    def __init__(self, database: str = 'database.db'):
        self.con = sqlite3.connect(database, check_same_thread=False)
        self.cur = self.con.cursor()
        self.con.execute('PRAGMA foreign_keys=ON')
        self.__database_init()

    @global_thread_safe
    def create_experiment(self, name: str) -> Tuple[UUID, bool]:
        try:
            self.cur.execute('INSERT INTO experiments (name) VALUES (?)', (name,))
            self.con.commit()
            return self.cur.lastrowid, False
        except sqlite3.IntegrityError:
            return self.get_experiment_id(name), True

    @global_thread_safe
    def create_generation(self, experiment_id: UUID) -> UUID:
        self.cur.execute('INSERT INTO generations (experiment_id) VALUES (?)',
                         (experiment_id,))
        self.con.commit()
        return self.cur.lastrowid

    @global_thread_safe
    def experiment_exist(self, experiment_id: UUID) -> bool:
        res = self.cur.execute('SELECT id FROM experiments WHERE id = ?',
                               (experiment_id,))
        return res.fetchone() is not None

    @global_thread_safe
    def store_population(self, generation_id: UUID, individuals: List[IndividualValue[T]]):
        values = [(generation_id, json.dumps(ind.encoding), ind.fitness) for ind in individuals]
        self.cur.executemany('''
        INSERT INTO individuals (generation_id, encoding, fitness) 
        VALUES (?, ?, ?)''', values)
        self.con.commit()

    @global_thread_safe
    def store_individual_fitness(self, individual_id: UUID, fitness: FitnessScore):
        self.cur.execute('UPDATE individuals SET fitness = ? WHERE id = ?',
                         (fitness, individual_id))
        self.con.commit()

    @global_thread_safe
    def get_experiment_id(self, experiment_name: str) -> UUID | None:
        q = self.cur.execute('SELECT id FROM experiments WHERE name = ?',
                             (experiment_name,))
        res = q.fetchone()
        return None if not res else res[0]

    @global_thread_safe
    def get_latest_generation_id(self, experiment_id: UUID) -> UUID | None:
        q = self.cur.execute('''
        SELECT id FROM generations
        WHERE experiment_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        ''', (experiment_id,))
        res = q.fetchone()
        return None if not res else res[0]

    @global_thread_safe
    def get_individual(self, individual_id: UUID) -> IndividualEntity[T] | None:
        q = self.cur.execute('''
        SELECT id, encoding, fitness FROM individuals WHERE id = ?
        ''', (individual_id,))
        res = q.fetchone()
        if not res:
            return None
        _id, raw_encoding, fitness = res
        encoding = json.loads(raw_encoding)
        return IndividualEntity[T](id=_id, encoding=encoding, fitness=fitness)

    @global_thread_safe
    def get_population(self, generation_id: UUID) -> List[IndividualEntity[T]]:
        res = self.cur.execute('''
        SELECT id, encoding, fitness FROM individuals WHERE generation_id = ?
        ''', (generation_id,))
        return self.__parse_to_entities(res.fetchall())

    @global_thread_safe
    def get_non_evaluated_individuals(self, generation_id: UUID) -> List[IndividualEntity[T]]:
        res = self.cur.execute('''
        SELECT id, encoding, fitness 
        FROM individuals 
        WHERE generation_id = ? AND fitness IS NULL
        ''', (generation_id,))
        return self.__parse_to_entities(res.fetchall())

    @global_thread_safe
    def count_generations(self, experiment_id: UUID) -> int:
        q = self.cur.execute('''
        SELECT COUNT(*)
        FROM generations
        WHERE experiment_id = ?
        ''', (experiment_id,))
        res = q.fetchone()
        return 0 if not res else res[0]

    @global_thread_safe
    def __database_init(self):
        setup_script_path = os.path.join(os.path.dirname(__file__), self.__SETUP_SCRIPT)
        with open(setup_script_path, 'r') as f:
            commands = f.readlines()
            cmd_string = f'BEGIN; {''.join(commands)} COMMIT;'
            self.cur.executescript(cmd_string)

    @staticmethod
    def __parse_to_entities(records):
        try:
            return [IndividualEntity[T](id=_id, encoding=json.loads(encoding), fitness=fitness)
                    for _id, encoding, fitness in records]
        except:
            return [IndividualEntity[T](id=_id, encoding=encoding, fitness=fitness)
                    for _id, encoding, fitness in records]
