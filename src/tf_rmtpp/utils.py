from tensorflow.contrib.keras import preprocessing
import itertools
import os
import tensorflow as tf
import numpy as np


pad_sequences = preprocessing.sequence.pad_sequences


def create_dir(dirname):
    """Creates a directory if it does not already exist."""
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def read_data(event_train_file, event_test_file, time_train_file, time_test_file):
    """Read data from given files and return it as a dictionary."""

    with open(event_train_file, 'r') as in_file:
        eventTrain = [[int(y) for y in x.strip().split()] for x in in_file]

    with open(event_test_file, 'r') as in_file:
        eventTest = [[int(y) for y in x.strip().split()] for x in in_file]

    with open(time_train_file, 'r') as in_file:
        timeTrain = [[float(y) for y in x.strip().split()] for x in in_file]

    with open(time_test_file, 'r') as in_file:
        timeTest = [[float(y) for y in x.strip().split()] for x in in_file]

    assert len(timeTrain) == len(eventTrain)
    assert len(eventTest) == len(timeTest)

    # nb_samples = len(eventTrain)
    # max_seqlen = max(len(x) for x in eventTrain)
    unique_samples = set()

    for x in eventTrain + eventTest:
        unique_samples = unique_samples.union(x)

    maxTime = max(itertools.chain((max(x) for x in timeTrain), (max(x) for x in timeTest)))
    minTime = min(itertools.chain((min(x) for x in timeTrain), (min(x) for x in timeTest)))
    # minTime, maxTime = 0, 1

    eventTrainIn = [x[:-1] for x in eventTrain]
    eventTrainOut = [x[1:] for x in eventTrain]
    timeTrainIn = [[(y - minTime) / (maxTime - minTime) for y in x[:-1]] for x in timeTrain]
    timeTrainOut = [[(y - minTime) / (maxTime - minTime) for y in x[1:]] for x in timeTrain]

    train_event_in_seq = pad_sequences(eventTrainIn, padding='post')
    train_event_out_seq = pad_sequences(eventTrainOut, padding='post')
    train_time_in_seq = pad_sequences(timeTrainIn, dtype=float, padding='post')
    train_time_out_seq = pad_sequences(timeTrainOut, dtype=float, padding='post')

    eventTestIn = [x[:-1] for x in eventTest]
    eventTestOut = [x[1:] for x in eventTest]
    timeTestIn = [[(y - minTime) / (maxTime - minTime) for y in x[:-1]] for x in timeTest]
    timeTestOut = [[(y - minTime) / (maxTime - minTime) for y in x[1:]] for x in timeTest]

    test_event_in_seq = pad_sequences(eventTestIn, padding='post')
    test_event_out_seq = pad_sequences(eventTestOut, padding='post')
    test_time_in_seq = pad_sequences(timeTestIn, dtype=float, padding='post')
    test_time_out_seq = pad_sequences(timeTestOut, dtype=float, padding='post')

    return {
        'train_event_in_seq': train_event_in_seq,
        'train_event_out_seq': train_event_out_seq,

        'train_time_in_seq': train_time_in_seq,
        'train_time_out_seq': train_time_out_seq,

        'test_event_in_seq': test_event_in_seq,
        'test_event_out_seq': test_event_out_seq,

        'test_time_in_seq': test_time_in_seq,
        'test_time_out_seq': test_time_out_seq,

        'num_categories': len(unique_samples)
    }


def variable_summaries(var, name=None):
    """Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
    if name is None:
        name = var.name.split('/')[-1][:-2]

    with tf.name_scope('summaries-' + name):
        mean = tf.reduce_mean(var)
        tf.summary.scalar('mean', mean)
        with tf.name_scope('stddev'):
            stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        tf.summary.scalar('stddev', stddev)
        tf.summary.scalar('max', tf.reduce_max(var))
        tf.summary.scalar('min', tf.reduce_min(var))
        tf.summary.histogram('histogram', var)


def mae(time_preds, time_true):
    """Calculates the MAE between the provided and the given time, ignoring the inf
    and nans. Returns both the MAE and the number of items considered."""
    is_finite = np.isfinite(time_preds)
    return np.mean(np.abs(time_preds - time_true)[is_finite]), np.sum(is_finite)


def acc(event_preds, event_true):
    """Returns the accuracy of the event prediction."""
    return np.sum(event_preds == event_true) / event_true.shape[0]
