import logging
import os
import sys
from mock import (
    Mock, patch
)
from pytest import (
    raises, fixture
)

from ..test_helper import argv_kiwi_tests

import kiwi
from kiwi.tasks.image_resize import ImageResizeTask

from kiwi.exceptions import (
    KiwiImageResizeError,
    KiwiSizeError,
    KiwiConfigFileNotFound
)


class TestImageResizeTask:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def setup(self):
        sys.argv = [
            sys.argv[0], '--profile', 'vmxSimpleFlavour', '--type', 'oem',
            'image', 'resize', '--target-dir', 'target_dir', '--size', '20g',
            '--root', '../data/root-dir'
        ]
        self.abs_root_dir = os.path.abspath('../data/root-dir')

        kiwi.tasks.image_resize.Help = Mock(
            return_value=Mock()
        )

        self.firmware = Mock()
        self.firmware.get_partition_table_type = Mock(
            return_value='gpt'
        )
        self.partitioner = Mock()
        self.loop_provider = Mock()
        kiwi.tasks.image_resize.FirmWare = Mock(
            return_value=self.firmware
        )
        kiwi.tasks.image_resize.LoopDevice = Mock(
            return_value=self.loop_provider
        )
        kiwi.tasks.image_resize.Partitioner = Mock(
            return_value=self.partitioner
        )

        self.task = ImageResizeTask()

    def teardown(self):
        sys.argv = argv_kiwi_tests

    def _init_command_args(self):
        self.task.command_args = {}
        self.task.command_args['help'] = False
        self.task.command_args['resize'] = False
        self.task.command_args['--target-dir'] = 'target_dir'
        self.task.command_args['--size'] = '42g'
        self.task.command_args['--root'] = '../data/root-dir'

    def test_process_no_root_directory_specified(self):
        self.task.command_args['--root'] = None
        with raises(KiwiConfigFileNotFound):
            self.task.process()

    @patch('kiwi.tasks.image_resize.DiskFormat.new')
    def test_process_no_raw_disk_found(self, mock_DiskFormat):
        image_format = Mock()
        image_format.has_raw_disk.return_value = False
        mock_DiskFormat.return_value = image_format
        self._init_command_args()
        self.task.command_args['resize'] = True
        with raises(KiwiImageResizeError):
            self.task.process()

    @patch('kiwi.tasks.image_resize.DiskFormat.new')
    def test_process_unsupported_size_format(self, mock_DiskFormat):
        image_format = Mock()
        image_format.has_raw_disk.return_value = True
        mock_DiskFormat.return_value = image_format
        self._init_command_args()
        self.task.command_args['--size'] = '20x'
        self.task.command_args['resize'] = True
        with raises(KiwiSizeError):
            self.task.process()

    @patch('kiwi.tasks.image_resize.DiskFormat.new')
    def test_process_image_resize_gb(self, mock_DiskFormat):
        image_format = Mock()
        image_format.resize_raw_disk.return_value = True
        mock_DiskFormat.return_value = image_format
        self._init_command_args()
        self.task.command_args['resize'] = True
        self.task.process()
        self.loop_provider.create.assert_called_once_with(overwrite=False)
        self.partitioner.resize_table.assert_called_once_with()
        image_format.resize_raw_disk.assert_called_once_with(
            42 * 1024 * 1024 * 1024
        )
        image_format.create_image_format.assert_called_once_with()

    @patch('kiwi.tasks.image_resize.DiskFormat.new')
    def test_process_image_resize_mb(self, mock_DiskFormat):
        image_format = Mock()
        image_format.resize_raw_disk.return_value = True
        mock_DiskFormat.return_value = image_format
        self._init_command_args()
        self.task.command_args['resize'] = True
        self.task.command_args['--size'] = '42m'
        self.task.process()
        self.loop_provider.create.assert_called_once_with(overwrite=False)
        self.partitioner.resize_table.assert_called_once_with()
        image_format.resize_raw_disk.assert_called_once_with(
            42 * 1024 * 1024
        )
        image_format.create_image_format.assert_called_once_with()

    @patch('kiwi.tasks.image_resize.DiskFormat.new')
    def test_process_image_resize_bytes(self, mock_DiskFormat):
        image_format = Mock()
        image_format.resize_raw_disk.return_value = True
        mock_DiskFormat.return_value = image_format
        self._init_command_args()
        self.task.command_args['resize'] = True
        self.task.command_args['--size'] = '42'
        self.task.process()
        self.loop_provider.create.assert_called_once_with(overwrite=False)
        self.partitioner.resize_table.assert_called_once_with()
        image_format.resize_raw_disk.assert_called_once_with(
            42
        )
        image_format.create_image_format.assert_called_once_with()

    @patch('kiwi.tasks.image_resize.DiskFormat.new')
    def test_process_image_resize_not_needed(self, mock_DiskFormat):
        image_format = Mock()
        image_format.resize_raw_disk.return_value = False
        mock_DiskFormat.return_value = image_format
        self._init_command_args()
        self.task.command_args['resize'] = True
        self.task.command_args['--size'] = '42'
        with self._caplog.at_level(logging.INFO):
            self.task.process()
            self.loop_provider.create.assert_called_once_with(overwrite=False)
            self.partitioner.resize_table.assert_called_once_with()
            image_format.resize_raw_disk.assert_called_once_with(
                42
            )
            assert 'Loading XML description' in self._caplog.text
            assert '--> loaded {0}'.format(
                os.sep.join([self.abs_root_dir, 'image', 'config.xml'])
            ) in self._caplog.text
            assert '--> Selected build type: oem' in self._caplog.text
            assert '--> Selected profiles: vmxSimpleFlavour' in self._caplog.text
            assert 'Resizing raw disk to 42 bytes' in self._caplog.text
            assert 'Raw disk is already at 42 bytes' in self._caplog.text

    def test_process_image_resize_help(self):
        self._init_command_args()
        self.task.command_args['help'] = True
        self.task.command_args['resize'] = True
        self.task.process()
        self.task.manual.show.assert_called_once_with(
            'kiwi::image::resize'
        )
